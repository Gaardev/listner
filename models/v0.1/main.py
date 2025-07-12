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

model = whisper.load_model("base")
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

class VoiceSession:
    def __init__(self, user, channel):
        pass

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def start_recording(self):
        pass

    async def stop_recording(self):
        pass

class AudioRecorder:
    def __init__(self, voice_client):
        pass

    async def record(self):
        pass

    def get_audio_chunk(self):
        pass


class TranscriptionManager:
    def __init__(self):
        self.queue = ChunkQueue()
        self.transcribed_results = []
        
    async def transcribe_chunk(self, audio_chunk):
        pass

    async def worker(self):
        pass

class ChunkQueue:
    def __init__(self):
        pass

    def add(self, chunk):
        pass

    def get(self):
        pass

    def is_empty(self):
        pass
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
    name="join",
    description="Join a voice channel"
)
@app_commands.describe(channel="Choose a voice channel")
async def sayhello(interaction: discord.Interaction, channel: discord.VoiceChannel):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
    await channel.connect()
    await interaction.response.send_message(f"Joined: {channel.name}", ephemeral=True)

@bot.tree.command(
    name="leave",
    description="Leave a voice channel"
)
@app_commands.describe()
async def sayhello(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client and voice_client.is_connected():
        channel_name = voice_client.channel.name
        await voice_client.disconnect()
        await interaction.response.send_message(f"Disconnected from {channel_name}", ephemeral=True)
    else:
        await interaction.response.send_message("Not in a voice channel", ephemeral=True)

@bot.event
async def on_ready():
    guild = discord.Object(id=1387414175952932984)
    bot.tree.clear_commands(guild=guild)
    await bot.tree.sync()
    print("Commands synced to test guild")
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) - slash commands synced")

bot.run(DISCORD_BOT_TOKEN)