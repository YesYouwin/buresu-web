import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread


# -----------------------------
# KEEP ALIVE SERVER
# -----------------------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()


# -----------------------------
# ENV VARIABLES
# -----------------------------

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))


# -----------------------------
# BOT SETUP
# -----------------------------

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# -----------------------------
# LOAD COMMANDS
# -----------------------------

async def setup_hook():

    print("Loading command modules...")

    extensions = [
        "commands.misc_commands.ping",
        "commands.misc_commands.server_info",
        "commands.misc_commands.user_info",
        "commands.players.player_logs",
        "commands.scrims.scrim_schedule",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded {ext}")
        except Exception as e:
            print(f"Failed to load {ext}: {e}")


bot.setup_hook = setup_hook


# -----------------------------
# READY EVENT
# -----------------------------

@bot.event
async def on_ready():

    guild = discord.Object(id=GUILD_ID)

    print("Clearing old commands...")
    bot.tree.clear_commands(guild=guild)

    print("Syncing commands...")
    await bot.tree.sync(guild=guild)

    print(f"Logged in as {bot.user}")
    print("Commands synced to development server.")


# -----------------------------
# START BOT
# -----------------------------

keep_alive()
bot.run(TOKEN)
