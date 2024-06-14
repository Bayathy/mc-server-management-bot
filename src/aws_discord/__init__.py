from dotenv import load_dotenv
import discord
import boto3

load_dotenv()

import os

intent = discord.Intents.all()

client = discord.Client(intents=intent)

ec2 = boto3.client(
    "ec2",
    region_name="ap-south-1",
)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    print(message.content)

    if message.content.startswith("!start"):
        response = ec2.start_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
        instance_running = False
        while not instance_running:
            instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
            state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
            if state == "running":
                instance_running = True
                await message.channel.send("Instance is now running")
        instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
        ip = instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]

        await message.channel.send(f"Instance IP: {ip}")

    if message.content.startswith("!stop"):
        response = ec2.stop_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
        instance_stopped = False
        while not instance_stopped:
            instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
            state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
            if state == "stopped":
                instance_stopped = True
                await message.channel.send("Instance is now stopped")
    
    if message.content.startswith("!status"):
        instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
        state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
        await message.channel.send(f"Instance is {state}")

    if message.content.startswith("!ip"):
        instance = ec2.describe_instances(InstanceIds=[os.getenv("INSTANCE_ID")])
        ip = instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        await message.channel.send(f"Instance IP: {ip}")

# Botの起動とDiscordサーバーへの接続
client.run(os.getenv("TOKEN"))
