import dotenv
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

model = whisper.load_model("small")  # Or "medium" if you're switching later
audio_queue = queue.Queue()

# -- GETTING ENV -- #

dotenv.load_dotenv("tokens.env")

DISCORD_BOT_TOKEN = os.getenv("APP_TOKEN")
APPLICATION_ID = os.getenv("APP_ID")
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUB_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

GEMNI_API_KEY = os.getenv("GEMNI_API")

# -- SETTING UP CLASSES -- #

class MyVoiceClient(discord.VoiceClient):
    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.audio_buffer = bytearray()
        self.task = None
        self._recording = False
        self.processing_thread = threading.Thread(target=self.process_audio_queue, daemon=True)
        self.processing_thread.start()

    async def on_voice_packet(self, packet):
        if self._recording:
            self.audio_buffer.extend(packet.data)

    async def start_recording(self):
        self._recording = True
        while self._recording:
            await asyncio.sleep(5)
            if self.audio_buffer:
                chunk = bytes(self.audio_buffer)
                self.audio_buffer = bytearray()
                audio_queue.put(chunk)

    def stop_recording(self):
        self._recording = False
        if self.task and not self.task.done():
            self.task.cancel()

    def process_audio_queue(self):
        while True:
            chunk = audio_queue.get()
            if chunk is None:
                break

            try:
                # Save chunk to a temp file
                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                raw_path = f"temp_{timestamp}.pcm"
                wav_path = f"temp_{timestamp}.wav"

                with open(raw_path, "wb") as f:
                    f.write(chunk)

                # Convert raw PCM to WAV (assumes 16-bit, 48kHz, mono)
                os.system(f"ffmpeg -f s16le -ar 48000 -ac 1 -i {raw_path} {wav_path} -y")

                # Transcribe using Whisper
                result = model.transcribe(wav_path)

                # Save to JSON
                with open("transcription.json", "a", encoding="utf-8") as f:
                    json.dump(result, f)
                    f.write("\n")

                # Save to TXT
                with open("transcription.txt", "a", encoding="utf-8") as f:
                    f.write(result["text"] + "\n")

            finally:
                if os.path.exists(raw_path):
                    os.remove(raw_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)


# -- DEFINING GENAI -- #

def gemni(payload, API_KEY):
    client = genai.Client(api_key=API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=payload,
        temperature=0.7
    )
    print(response.text)
    callback = response.text
    return callback

# -- SETTING UP BOT SETTINGS -- #

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix=None, intents=discord.Intents.all())
tree = bot.tree

# -- SLASH COMMANDS -- #

@tree.command(
    name="join",
    description="Join the voice channel you are in"
)
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        vc = await channel.connect(cls=MyVoiceClient)
        await interaction.response.send_message(f"Joined {channel.name}", ephemeral=True)
    else:
        await interaction.response.send_message("You are not in a voice channel", ephemeral=True)

@tree.command(
    name="record",
    description="Start recording audio in the current voice channel"
)
async def record(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and isinstance(vc, MyVoiceClient):
        if vc.task is None or vc.task.done():
            vc.task = asyncio.create_task(vc.start_recording())
            await interaction.response.send_message("Recording started.", ephemeral=True)
        else:
            await interaction.response.send_message("Recording is already in progress.", ephemeral=True)
    else:
        await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)

@tree.command(
    name="stoprecording",
    description="Stop recording audio in the current voice channel"
)
async def stoprecording(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and isinstance(vc, MyVoiceClient):
        vc.stop_recording()
        await interaction.response.send_message("Recording stopped.", ephemeral=True)
    else:
        await interaction.response.send_message("Not currently recording.", ephemeral=True)

@tree.command(
    name="leave",
    description="Leave the voice channel"
)
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Left the voice channel", ephemeral=True)
    else:
        await interaction.response.send_message("I am not in any voice channel", ephemeral=True)

# -- BOT EVENTS -- #

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) - slash commands synced")

bot.run(DISCORD_BOT_TOKEN)