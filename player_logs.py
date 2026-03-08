import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils import is_staff
import json
import os
import io
import asyncio

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload


service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build("drive", "v3", credentials=credentials)

FILE_NAME = "player_logs.json"
FOLDER_ID = "1BqiW_4RmbYMqmL1EzUKXA1Opj7PviDH5"


def get_file_id():
    try:
        results = service.files().list(
            q=f"name='{FILE_NAME}' and '{FOLDER_ID}' in parents",
            spaces="drive",
            fields="files(id,name)"
        ).execute()

        files = results.get("files", [])
        return files[0]["id"] if files else None

    except Exception as e:
        print("Drive lookup error:", e)
        return None


def load_logs():
    try:
        file_id = get_file_id()

        if not file_id:
            return []

        request = service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        fh.seek(0)

        try:
            return json.load(fh)
        except:
            return []

    except Exception as e:
        print("Load logs error:", e)
        return []


def save_logs(logs):
    try:

        file_id = get_file_id()

        data = json.dumps(logs, indent=4)

        fh = io.BytesIO(data.encode())

        media = MediaIoBaseUpload(
            fh,
            mimetype="application/json",
            resumable=True
        )

        if file_id:

            service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()

        else:

            file_metadata = {
                "name": FILE_NAME,
                "parents": [FOLDER_ID]
            }

            service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

    except Exception as e:
        print("Save logs error:", e)


class PlayerLogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="drivetest")
    async def drivetest(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        await asyncio.to_thread(save_logs, [{"test": "working"}])

        await interaction.followup.send(
            "✅ Drive connection successful",
            ephemeral=True
        )


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
            parsed_date = datetime.strptime(date, "%d/%m/%Y")
            day = parsed_date.strftime("%A")
            formatted_date = f"{date} [{day}]"

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


        logs = await asyncio.to_thread(load_logs)

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


        await asyncio.to_thread(save_logs, logs)


        await interaction.followup.send(
            "✅ Player log created",
            ephemeral=True
        )


    @app_commands.command(name="playerhistory", description="Retrieve player history")
    @is_staff()
    async def playerhistory(self, interaction: discord.Interaction, search: str):

        await interaction.response.defer(ephemeral=True)

        logs = await asyncio.to_thread(load_logs)

        results = []

        for log in logs:

            if (
                search == log["discord_id"]
                or search.lower() in log["ign"].lower()
                or search in log["date"]
            ):
                results.append(log)


        if not results:

            await interaction.followup.send(
                "❌ No logs found",
                ephemeral=True
            )
            return


        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


        await interaction.followup.send(
            f"📜 Found {len(results)} log(s) for `{search}`",
            ephemeral=True
        )


        for log in results:

            try:
                user = await self.bot.fetch_user(int(log["discord_id"]))
                mention = user.mention
                avatar = user.display_avatar.url
            except:
                mention = f"<@{log['discord_id']}>"
                avatar = None


            if log["action"] in ["Recruitment", "Promotion"]:
                emoji = "<:Plus:1438977678890766517>"
                color = discord.Color.green()
            else:
                emoji = "<:Negative:1438979843252289656>"
                color = discord.Color.red()


            try:
                parsed_date = datetime.strptime(log["date"], "%d/%m/%Y")
                day = parsed_date.strftime("%A")
                formatted_date = f"{log['date']} [{day}]"
            except:
                formatted_date = log["date"]


            embed = discord.Embed(
                description=f"""
{divider}
**{emoji} {log['action']}**

{mention}

**IGN -** [{log['ign']}]({log['trackerid']})

**{log['team1']} ➜ {log['team2']}**

**Date -** {formatted_date}

**Reason —** *{log['reason']}*
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
