import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils import is_staff
import sqlite3
import os

DB_FILE = "player_logs.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        discord_id TEXT,
        ign TEXT,
        team1 TEXT,
        team2 TEXT,
        date TEXT,
        trackerid TEXT,
        reason TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_log(action, discord_id, ign, team1, team2, date, trackerid, reason):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO player_logs
    (action, discord_id, ign, team1, team2, date, trackerid, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        action,
        discord_id,
        ign,
        team1,
        team2,
        date,
        trackerid,
        reason
    ))

    conn.commit()
    conn.close()


def search_logs(search):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT action, discord_id, ign, team1, team2, date, trackerid, reason
    FROM player_logs
    WHERE discord_id = ?
    OR LOWER(ign) LIKE ?
    OR date LIKE ?
    """, (
        search,
        f"%{search.lower()}%",
        f"%{search}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


class PlayerLogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        init_db()


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

        await interaction.response.defer(ephemeral=True)

        try:
            parsed = datetime.strptime(date, "%d/%m/%Y")
            formatted_date = f"{date} [{parsed.strftime('%A')}]"

        except ValueError:
            await interaction.followup.send(
                "❌ Invalid date format. Use **DD/MM/YYYY**",
                ephemeral=True
            )
            return


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

        log_channel = self.bot.get_channel(1443545539445653604)

        if log_channel:
            await log_channel.send(embed=embed)


        save_log(
            action.value,
            str(discordname.id),
            ign,
            team1,
            team2,
            date,
            trackerid,
            reason
        )

        await interaction.followup.send(
            "✅ Player log created",
            ephemeral=True
        )


    @app_commands.command(name="playerhistory", description="Retrieve player history")
    @is_staff()
    async def playerhistory(self, interaction: discord.Interaction, search: str):

        await interaction.response.defer(ephemeral=True)

        rows = search_logs(search)

        if not rows:
            await interaction.followup.send(
                "❌ No logs found",
                ephemeral=True
            )
            return


        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        await interaction.followup.send(
            f"📜 Found {len(rows)} log(s) for `{search}`",
            ephemeral=True
        )


        for action, discord_id, ign, team1, team2, date, trackerid, reason in rows:

            try:
                user = await self.bot.fetch_user(int(discord_id))
                mention = user.mention
                avatar = user.display_avatar.url
            except:
                mention = f"<@{discord_id}>"
                avatar = None


            if action in ["Recruitment", "Promotion"]:
                emoji = "<:Plus:1438977678890766517>"
                color = discord.Color.green()
            else:
                emoji = "<:Negative:1438979843252289656>"
                color = discord.Color.red()


            try:
                parsed = datetime.strptime(date, "%d/%m/%Y")
                formatted_date = f"{date} [{parsed.strftime('%A')}]"
            except:
                formatted_date = date


            embed = discord.Embed(
                description=f"""
{divider}
**{emoji} {action}**

{mention}

**IGN -** [{ign}]({trackerid})

**{team1} ➜ {team2}**

**Date -** {formatted_date}

**Reason —** *{reason}*
{divider}
""",
                color=color
            )

            if avatar:
                embed.set_thumbnail(url=avatar)

            embed.set_footer(text=f"© Buresu • {datetime.now().year}")

            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PlayerLogs(bot))
