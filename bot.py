
import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

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

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def setup_hook():
    print("Loading command modules...")
    for root, dirs, files in os.walk("./commands"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                path = os.path.join(root, file)
                module = (
                    os.path.relpath(path, ".")
                    .replace("\\", ".")
                    .replace("/", ".")
                    .replace(".py", "")
                )
                try:
                    await bot.load_extension(module)
                    print(f"Loaded {module}")
                except Exception as e:
                    print(f"Failed to load {module}: {e}")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.clear_commands(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")
    print("Commands synced to development server.")

keep_alive()
bot.run(TOKEN)
