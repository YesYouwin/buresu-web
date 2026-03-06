import discord
from discord import app_commands
from discord.ext import commands
import os

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
    timezone="Timezone"
)

# DROPDOWNS
@app_commands.choices(

    scrim_type=[
        app_commands.Choice(name="In-Houses", value="In-Houses"),
        app_commands.Choice(name="Scrim", value="Scrim"),
        app_commands.Choice(name="Tournament", value="Tournament")
    ],

    map_name=[
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
    timezone: app_commands.Choice[str]
):

    message = f"""
# 📅 SCRIM SCHEDULE

> **Scrim Type:** {scrim_type.value}
> **Teams:** {team_a} VS {team_b}
> **Time:** {time} {timezone.value}
> **Date:** {date}
> **Map:** {map_name.value}

⚠️ **Note:**  
The <@1479519180054335548> of the team is responsible for any player's absence.  
Players must inform beforehand so the event runs smoothly.
"""

    await interaction.response.send_message(message)


bot.run(TOKEN)
