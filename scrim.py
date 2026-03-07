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
        team_a="First Team (role or name)",
        team_b="Second Team (role or name)",
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

        guild = interaction.guild

        # Try to find roles for team_a and team_b
        team_a_role = discord.utils.get(guild.roles, name=team_a)
        team_b_role = discord.utils.get(guild.roles, name=team_b)

        # Keep original mentionable state
        team_a_original = team_a_role.mentionable if team_a_role else None
        team_b_original = team_b_role.mentionable if team_b_role else None

        # Make roles mentionable if needed
        if team_a_role and not team_a_role.mentionable:
            await team_a_role.edit(mentionable=True)
        if team_b_role and not team_b_role.mentionable:
            await team_b_role.edit(mentionable=True)

        # Determine display names
        team_a_display = team_a_role.mention if team_a_role else team_a
        team_b_display = team_b_role.mention if team_b_role else team_b

        # Ping roles first if they exist
        ping_message = ""
        if team_a_role:
            ping_message += f"{team_a_display} "
        if team_b_role:
            ping_message += f"{team_b_display} "

        if ping_message:
            await interaction.response.send_message(ping_message, ephemeral=False)
        else:
            await interaction.response.send_message("Scrim scheduled!", ephemeral=False)

        # Build the plain text schedule
        schedule_message = (
            f"# **{scrim_type.value} SCHEDULE**\n\n"
            f"**Teams:** {team_a_display} VS {team_b_display}\n"
            f"**Time:** {time} {timezone.value}\n"
            f"**Day/Date:** {formatted_date}\n"
            f"**Format:** {format.value}\n"
            f"**Map:** {map_name}\n\n"
            f"⚠️ **Note:**\n"
            f"- <@&1442456929321619556> are responsible for any player's absence.\n"
            f"- Players must inform about any discrepancy beforehand so the event runs smoothly."
        )

        # Send the schedule
        await interaction.followup.send(schedule_message)

        # Revert roles back to original mentionable state
        if team_a_role and team_a_original is not None and team_a_role.mentionable != team_a_original:
            await team_a_role.edit(mentionable=team_a_original)
        if team_b_role and team_b_original is not None and team_b_role.mentionable != team_b_original:
            await team_b_role.edit(mentionable=team_b_original)


async def setup(bot):
    await bot.add_cog(Scrim(bot))
