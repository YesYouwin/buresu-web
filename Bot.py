import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
    

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="scrim", description="Create a Scrim Schedule")
@app_commands.describe(
    scrim_type="Type of Scrim",
    team_a="First Team",
    team_b="Second Team",
    time="Match Time",
    date="Match Date",
    map_name="Map",
    timezone="Timezone",
    format="Format"
)

# DROPDOWNS
@app_commands.choices(

    scrim_type=[
        app_commands.Choice(name="In-Houses", value="IN-HOUSES"),
        app_commands.Choice(name="Scrim", value="SCRIM"),
        app_commands.Choice(name="Tournament", value="TOURNAMENT")
    ],

    map_name=[
        app_commands.Choice(name="TBD", value="To Be Decided through mapban.gg"),
        app_commands.Choice(name="Abyss", value="Abyss"),
        app_commands.Choice(name="Ascent", value="Ascent"),
        app_commands.Choice(name="Bind", value="Bind"),
        app_commands.Choice(name="Breeze", value="Breeze"),
        app_commands.Choice(name="Corrode", value="Corrode"),
        app_commands.Choice(name="Fracture", value="Fracture"),
        app_commands.Choice(name="Haven", value="Haven"),
        app_commands.Choice(name="Icebox", value="Icebox"),
        app_commands.Choice(name="Lotus", value="Lotus"),
        app_commands.Choice(name="Pearl", value="Pearl"),
        app_commands.Choice(name="Split", value="Split"),
        app_commands.Choice(name="Sunset", value="Sunset")
    ],

    timezone=[
        app_commands.Choice(name="IST", value="IST"),
        app_commands.Choice(name="SGT", value="SGT"),
        app_commands.Choice(name="GMT", value="GMT"),
        app_commands.Choice(name="PST", value="PST")
    ],

    format=[
        app_commands.Choice(name="BO1", value="Best Of 1 Map"),
        app_commands.Choice(name="BO3", value="Best Of 3 Maps"),
        app_commands.Choice(name="BO5", value="Best Of 5 Maps"),
        app_commands.Choice(name="MR24", value="Max Rounds 24")
    ]
    
)

async def scrim(
    interaction: discord.Interaction,
    scrim_type: app_commands.Choice[str],
    team_a: str,
    team_b: str,
    time: str,
    date: str,
    map_name: app_commands.Choice[str],
    timezone: app_commands.Choice[str],
    format: app_commands.Choice[str]
):

    try:
        parsed_date = datetime.strptime(date, "%d/%m/%Y")
        day_name = parsed_date.strftime("%A")
        formatted_date = f"{date} [{day_name}]"
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid date format. Please use **DD/MM/YYYY** (example: 07/03/2026)",
            ephemeral=True
        )
        return

    message = f"""
# 📅 {scrim_type.value} SCHEDULE

> **Teams:** {team_a} VS {team_b}
> **Time:** {time} {timezone.value}
> **Day/Date:** {formatted_date}
> **Format:** {format.value}
> **Map:** {map_name.value}

⚠️ **Note**  
- The <@&1442456929321619556> of the team is responsible for any player's absence.  
- Players must inform about any discrepancy beforehand so the event runs smoothly.
"""

    await interaction.response.send_message(message)

keep_alive()
bot.run(TOKEN)
