FROM python:3.12.3-slim-bookworm

RUN apt update && \
    apt install -y curl && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

ARG USERNAME=ryeuser
RUN useradd ${USERNAME} --create-home
USER ${USERNAME}

WORKDIR /home/${USERNAME}/app

ENV RYE_HOME /home/${USERNAME}/.rye
ENV PATH ${RYE_HOME}/shims:${PATH}

RUN curl -sSf https://rye.astral.sh/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash


RUN mkdir -p /root/src
COPY . /root/src
WORKDIR /root/src

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=requirements.lock,target=requirements.lock \
    --mount=type=bind,source=requirements-dev.lock,target=requirements-dev.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    --mount=type=bind,source=README.md,target=README.md \
    rye sync --no-dev --no-lock

EXPOSE 8080

RUN . .venv/bin/activate


ENTRYPOINT ["python3", "./src/main.py"]