import discord
import os
from discord.ext import commands
import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
def convert_to_sgt(time_str):
    ist = datetime.datetime.strptime(time_str, "%I:%M%p")
    sgt = ist + datetime.timedelta(hours=2, minutes=30)
    return sgt.strftime("%I:%M %p")


@bot.command(name="game")
async def scrim(ctx, scrim_type, teams, time, timezone, date, map_name):

    try:

        team1, team2 = teams.split("Vs")

        sgt_time = convert_to_sgt(time)

        embed = discord.Embed(
            title="🎮 Scrim | Scrim Schedule",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Teams",
            value=f"{team1} VS {team2}",
            inline=False
        )

        embed.add_field(
            name="Time",
            value=f"{time} {timezone} / {sgt_time} SGT",
            inline=False
        )

        embed.add_field(
            name="Day/Date",
            value=date,
            inline=False
        )

        embed.add_field(
            name="Map",
            value=map_name,
            inline=False
        )

        embed.add_field(
            name="Note",
            value="The @IGL of the team is responsible for any player's absence. Please inform beforehand.",
            inline=False
        )

        await ctx.send(embed=embed)

    except:
        await ctx.send("Format error. Example:\n!game In-Houses Team1VsTeam2 7:30PM IST 21/10/2026 Split")
        
bot.run(TOKEN)

