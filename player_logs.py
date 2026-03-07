import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class PlayerLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="playerlogs", description="Create a formatted player log")

    @app_commands.choices(action=[
        app_commands.Choice(name="Recruitment", value="Recruitment"),
        app_commands.Choice(name="Promotion", value="Promotion"),
        app_commands.Choice(name="Relegation", value="Relegation"),
        app_commands.Choice(name="Removed", value="Removed")
    ])

    async def playerlogs(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        ign: str,
        discordname: discord.Member,
        date: str,
        team1: str,
        team2: str,
        trackerid: str,
        reason: str
    ):

        # Validate date
        try:
            parsed_date = datetime.strptime(date, "%d/%m/%Y")
            day_name = parsed_date.strftime("%A")
            formatted_date = f"{date} [{day_name}]"
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format. Use **DD/MM/YYYY** (example: 25/12/2025)",
                ephemeral=True
            )
            return


        if action.value in ["Recruitment", "Promotion"]:
            emoji = "<:Plus:1438977678890766517>"
            color = discord.Color.green()
        else:
            emoji = "<:Negative:1438979843252289656>"
            color = discord.Color.red()

        year = datetime.now().year
        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


        embed = discord.Embed(
            description=f"""
{divider}

{emoji} {action.value}

{discordname.mention}

**IGN -** [{ign}]({trackerid})

**{team1} ➜ {team2}**

**Date -** {formatted_date}

**Reason —** *{reason}*

{divider}
""",
            color=color
        )

        embed.set_thumbnail(url=discordname.display_avatar.url)
        embed.set_footer(text="© Buresu • *{year}*")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(PlayerLogs(bot))
