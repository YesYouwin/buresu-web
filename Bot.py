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
    map_name="Map(s) — If multiple, separate with commas",
    timezone="Timezone",
    format="Format"
)

@app_commands.choices(

    scrim_type=[
        app_commands.Choice(name="In-Houses", value="<:InHouses:1442182642920587324> IN-HOUSES"),
        app_commands.Choice(name="Scrim", value="<:Scrim:1456784764798374132> SCRIM"),
        app_commands.Choice(name="Tournament", value="<a:Red_Fire:1470755261676519436> TOURNAMENT")
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
    map_name: str,
    timezone: app_commands.Choice[str],
    format: app_commands.Choice[str]
):

    # Date validation
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

    # Split maps
    maps = [m.strip() for m in map_name.split(",")]

    # Determine required maps
    required_maps = 1

    if format.value == "Best Of 3 Maps":
        required_maps = 3
    elif format.value == "Best Of 5 Maps":
        required_maps = 5
    elif format.value == "Max Rounds 24":
        required_maps = 1

    # Validate map count
    if len(maps) != required_maps:
        await interaction.response.send_message(
            f"❌ {format.name} requires **{required_maps} maps**.\n"
            f"Example: `Ascent, Haven, Split`",
            ephemeral=True
        )
        return

    # Format map list
    map_list = "\n".join([f"> Map {i+1}: {m}" for i, m in enumerate(maps)])

    message = f"""
# {scrim_type.value} SCHEDULE

> **Teams:** {team_a} VS {team_b}
> **Time:** {time} {timezone.value}
> **Day/Date:** {formatted_date}
> **Format:** {format.value}

> **Maps**
{map_list}

⚠️ **Note**  
- The <@&1442456929321619556> of the team is responsible for any player's absence.  
- Players must inform about any discrepancy beforehand so the event runs smoothly.
"""

    await interaction.response.send_message(message)

keep_alive()
bot.run(TOKEN)
