from dotenv import load_dotenv
import discord
from discord import app_commands
import boto3

load_dotenv()

import os

intent = discord.Intents.all()

MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))

ec2 = boto3.client(
    "ec2",
    region_name="ap-south-1",
)


class ManagementBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            intents=intents.all(),
        )

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = ManagementBot(intents=intents)


@client.event
async def on_ready():
    print(f"Bot is ready as {client.user}")


@client.tree.command()
async def mc_start(interaction: discord.Interaction):
    response = ec2.start_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
    instance_running = False
    await interaction.response.defer()
    while not instance_running:
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        if state == "running":
            instance_running = True

    instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
    ip = instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]

    await interaction.followup.send(
        f"Instance is now running\nIP: {ip}", ephemeral=True
    )


@client.tree.command()
async def mc_stop(interaction: discord.Interaction):
    await interaction.response.defer()
    response = ec2.stop_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
    instance_stopped = False
    while not instance_stopped:
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        print(state)
        if state == "stopping":
            instance_stopped = True
            await interaction.followup.send("Instance is now stopped", ephemeral=True)


@client.tree.command()
async def mc_status(interaction: discord.Interaction):
    await interaction.response.defer()
    instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
    state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
    await interaction.followup.send(f"Instance is {state}", ephemeral=True)


@client.tree.command()
async def mc_ip(interaction: discord.Interaction):
    await interaction.response.defer()
    instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
    if instance["Reservations"][0]["Instances"][0]["State"]["Name"] != "running":
        await interaction.response.send_message("Instance is not running")
        await interaction.followup.send("Instance is not running", ephemeral=True)
        return

    ip = instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    await interaction.followup.send(f"Instance IP: {ip}", ephemeral=True)


client.run(os.getenv("TOKEN"))
