import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils import is_staff
import json
import os


PLAYER_LOGS_FILE = "player_logs.json"


def load_logs():
    if not os.path.exists(PLAYER_LOGS_FILE):
        return []
    with open(PLAYER_LOGS_FILE, "r") as f:
        return json.load(f)


def save_logs(logs):
    with open(PLAYER_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)


class PlayerLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playerlogs", description="Create a formatted player log")
    @is_staff()
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
        discordname: discord.User,
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

        # Choose emoji and color
        if action.value in ["Recruitment", "Promotion"]:
            emoji = "<:Plus:1438977678890766517>"
            color = discord.Color.green()
        else:
            emoji = "<:Negative:1438979843252289656>"
            color = discord.Color.red()

        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        embed = discord.Embed(
            description=f"""
{divider}
**{emoji} {action.value}**

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
        embed.set_footer(text=f"© Buresu • {datetime.now().year}")

        # Send to log channel
        log_channel = self.bot.get_channel(1443545539445653604)
        if log_channel is None:
            await interaction.response.send_message("❌ Log channel not found.", ephemeral=True)
            return

        await log_channel.send(embed=embed)
        await interaction.response.send_message("✅ Player log created.", ephemeral=True)

        # Save log to JSON
        logs = load_logs()
        logs.append({
            "action": action.value,
            "discord_id": str(discordname.id),
            "ign": ign,
            "team1": team1,
            "team2": team2,
            "date": date,
            "trackerid": trackerid,
            "reason": reason
        })
        save_logs(logs)

    @app_commands.command(name="playerhistory", description="Retrieve player history")
    @is_staff()
    async def playerhistory(
        self,
        interaction: discord.Interaction,
        search: str
    ):
        logs = load_logs()
        results = []

        # Search by Discord ID, IGN, or Date
        for log in logs:
            if search == log["discord_id"] or search.lower() == log["ign"].lower() or search == log["date"]:
                results.append(log)

        if not results:
            await interaction.response.send_message("❌ No logs found for that search.", ephemeral=True)
            return

        # Create embed for results
        embed = discord.Embed(
            title=f"Player History for `{search}`",
            color=discord.Color.blue()
        )

        for log in results:
            embed.add_field(
                name=f"{log['action']} - {log['ign']}",
                value=f"**Discord ID:** <@{log['discord_id']}>\n"
                      f"**Teams:** {log['team1']} ➜ {log['team2']}\n"
                      f"**Date:** {log['date']}\n"
                      f"**Reason:** {log['reason']}\n"
                      f"[Tracker]({log['trackerid']})",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerLogs(bot))
