import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ----------------------------
# KEEP ALIVE SERVER
# ----------------------------

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------------------
# DISCORD BOT SETUP
# ----------------------------

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# LOAD COMMANDS FROM FOLDERS
# ----------------------------

async def setup_hook():

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

    await bot.tree.sync()
    print("Slash commands synced")

bot.setup_hook = setup_hook

# ----------------------------
# BOT READY EVENT
# ----------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ----------------------------
# START BOT
# ----------------------------

keep_alive()
bot.run(TOKEN)
