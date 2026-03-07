import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class Scrim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="scrim", description="Create a Scrim Schedule")
    @app_commands.describe(
        scrim_type="Type of Scrim",
        team_a="First Team",
        team_b="Second Team",
        time="Match Time",
        date="Match Date (DD/MM/YYYY)",
        map_name="Map name (admins type manually)",
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
        self,
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

        # Validate date
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
# {scrim_type.value} SCHEDULE

> **Teams:** {team_a} VS {team_b}
> **Time:** {time} {timezone.value}
> **Day/Date:** {formatted_date}
> **Format:** {format.value}
> **Map:** {map_name}

⚠️ **Note**  
- The <@&1442456929321619556> of the team is responsible for any player's absence.  
- Players must inform about any discrepancy beforehand so the event runs smoothly.
"""

        await interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(Scrim(bot))
