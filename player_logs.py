import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils import is_staff
import traceback
import asyncio
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os

# ----------------------------
# DATABASE CONNECTION
# ----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables!")

# Connection pool
pool = SimpleConnectionPool(
    1,
    10,
    DATABASE_URL,
    sslmode="require"
)

def get_conn():
    return pool.getconn()

def return_conn(conn):
    pool.putconn(conn)

# ----------------------------
# DATABASE FUNCTIONS
# ----------------------------
def save_log(action, discord_id, ign, team1, team2, date, trackerid, reason):
    conn = get_conn()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO player_logs
                (action, discord_id, ign, team1, team2, date, trackerid, reason)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (action, discord_id, ign, team1, team2, date, trackerid, reason),
            )

        conn.commit()

    finally:
        return_conn(conn)


def search_logs(search):
    conn = get_conn()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT action, discord_id, ign, team1, team2, date, trackerid, reason
                FROM player_logs
                WHERE discord_id::text = %s
                OR LOWER(ign) LIKE %s
                OR date LIKE %s
                ORDER BY id DESC
                """,
                (search, f"%{search.lower()}%", f"%{search}%"),
            )

            return cursor.fetchall()

    finally:
        return_conn(conn)

# ----------------------------
# COG
# ----------------------------
class PlayerLogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ------------------------
    # CREATE PLAYER LOG
    # ------------------------
    @app_commands.command(name="playerlogs", description="Create a formatted player log")
    @is_staff()
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Recruitment", value="Recruitment"),
            app_commands.Choice(name="Promotion", value="Promotion"),
            app_commands.Choice(name="Relegation", value="Relegation"),
            app_commands.Choice(name="Removed", value="Removed"),
        ]
    )
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
        reason: str,
    ):

        await interaction.response.defer(ephemeral=True)

        try:
            parsed = datetime.strptime(date, "%d/%m/%Y")
            formatted_date = f"{date} [{parsed.strftime('%A')}]"
        except ValueError:
            await interaction.followup.send(
                "❌ Invalid date format. Use **DD/MM/YYYY**", ephemeral=True
            )
            return

        emoji = (
            "<:Plus:1438977678890766517>"
            if action.value in ["Recruitment", "Promotion"]
            else "<:Negative:1438979843252289656>"
        )

        color = (
            discord.Color.green()
            if action.value in ["Recruitment", "Promotion"]
            else discord.Color.red()
        )

        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

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
            color=color,
        )

        embed.set_thumbnail(url=discordname.display_avatar.url)
        embed.set_footer(text=f"© Buresu • {datetime.now().year}")

        log_channel = self.bot.get_channel(1443545539445653604)

        if log_channel:
            await log_channel.send(embed=embed)

        try:
            await asyncio.to_thread(
                save_log,
                action.value,
                str(discordname.id),
                ign,
                team1,
                team2,
                date,
                trackerid,
                reason
            )
        except Exception as e:
            print("Database error:", e)

        await interaction.followup.send("✅ Player log created", ephemeral=True)

    # ------------------------
    # PLAYER HISTORY
    # ------------------------
    @app_commands.command(name="playerhistory", description="Retrieve player history")
    @is_staff()
    async def playerhistory(self, interaction: discord.Interaction, search: str):

        await interaction.response.defer(ephemeral=True)

        search = search.strip()

        if search.startswith("<@") and search.endswith(">"):
            search = search.replace("<@", "").replace(">", "").replace("!", "")

        try:
            rows = await asyncio.to_thread(search_logs, search)
        except Exception:
            error_msg = traceback.format_exc()

            print(error_msg)

            await interaction.followup.send(
                f"❌ Database Error:\n```{error_msg[:1900]}```",
                 ephemeral=True
            )
            return

        if not rows:
            await interaction.followup.send("❌ No logs found.", ephemeral=True)
            return

        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        await interaction.followup.send(
            f"📜 Found **{len(rows)}** log(s) for `{search}`", ephemeral=True
        )

        for action, discord_id, ign, team1, team2, date, trackerid, reason in rows:

            try:
                user = await self.bot.fetch_user(int(discord_id))
                mention = user.mention
                avatar = user.display_avatar.url
            except:
                mention = f"<@{discord_id}>"
                avatar = None

            emoji = (
                "<:Plus:1438977678890766517>"
                if action in ["Recruitment", "Promotion"]
                else "<:Negative:1438979843252289656>"
            )

            color = (
                discord.Color.green()
                if action in ["Recruitment", "Promotion"]
                else discord.Color.red()
            )

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
                color=color,
            )

            if avatar:
                embed.set_thumbnail(url=avatar)

            embed.set_footer(text=f"© Buresu • {datetime.now().year}")

            await interaction.followup.send(embed=embed, ephemeral=True)


# ----------------------------
# SETUP
# ----------------------------
async def setup(bot):
    await bot.add_cog(PlayerLogs(bot))
