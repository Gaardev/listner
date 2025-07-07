from dotenv import load_dotenv
import os
import discord
from discord import app_commands
from discord.ext import commands
import io
import asyncio

from google import genai

import threading
import queue
import json
import datetime
import whisper

# PERMISSION INTEGER: 328568269824 (USED FOR GETTING SAME PERMISSIONS EACH TIME YOU INVITE)

model = whisper.load_model("medium")
audio_queue = queue.Queue()

# -- GETTING ENV -- #

load_dotenv("/home/benjamin/Documents/repo/discord-bot/models/v0.1/tokens.env")

DISCORD_BOT_TOKEN = os.getenv("APP_TOKEN")
APPLICATION_ID = os.getenv("APP_ID")
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUB_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

GEMNI_API_KEY = os.getenv("GEMNI_API")

# -- SETTING UP CLASSES -- #



# -- DEFINING GENAI -- #

def gemni(payload, API_KEY):
    client = genai.Client(api_key=API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=payload,
        temperature=0.7
    )
    print(response.text)
    response = response.text
    return response

# -- DEFINING CLEINT AND TREE -- #

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=None, intents=intents)
tree = bot.tree

# -- SLASH COMMANDS -- #

@bot.tree.command(
    name="sayhello",
    description="Say hello in a specified voice channel"
)
@app_commands.describe(channel="Choose a voice channel")
async def sayhello(interaction: discord.Interaction, channel: discord.VoiceChannel):
    await interaction.response.send_message(f"Hello from {channel.name}!", ephemeral=True)

@bot.event
async def on_ready():
    guild = discord.Object(id=1387414175952932984)
    bot.tree.clear_commands(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Commands synced to test guild")
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) - slash commands synced")

bot.run(DISCORD_BOT_TOKEN)