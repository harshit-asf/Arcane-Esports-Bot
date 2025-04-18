import discord
from discord.ext import commands, tasks
import datetime
import os

TOKEN = os.getenv('MTM2MjExNzAyMTcyMjA4NzQyNA.GQkZtI.y8CuChv_-Z3jPVo1084-zP7Yaf_znRej1D2B6g')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

REGISTRATION_START = datetime.time(hour=12, minute=0)  # 12:00 PM
REGISTRATION_END = datetime.time(hour=14, minute=0)    # 2:00 PM
REGISTERED_ROLE = "Registered"

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    check_registration_time.start()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def helpme(ctx):
    embed = discord.Embed(title="Commands", description="List of commands", color=0x00ff00)
    embed.add_field(name="!register [team name]", value="Register your team during 12-2 PM", inline=False)
    embed.add_field(name="!ping", value="Bot responsiveness", inline=False)
    await ctx.send(embed=embed)

def is_registration_time():
    now = datetime.datetime.now().time()
    return REGISTRATION_START <= now <= REGISTRATION_END

@bot.command()
async def register(ctx, *, team_name: str = None):
    if not is_registration_time():
        await ctx.send("Registration is only allowed between 12:00 PM and 2:00 PM.")
        return

    if not team_name:
        await ctx.send("Please provide a team name: `!register MyTeamName`")
        return

    attachments = ctx.message.attachments
    if not attachments:
        await ctx.send("Please attach your team logo while registering.")
        return

    logo = attachments[0]
    role = discord.utils.get(ctx.guild.roles, name=REGISTERED_ROLE)
    if not role:
        role = await ctx.guild.create_role(name=REGISTERED_ROLE)

    await ctx.author.add_roles(role)

    # Log team registration
    channel = discord.utils.get(ctx.guild.text_channels, name="registrations")
    if not channel:
        channel = await ctx.guild.create_text_channel("registrations")

    embed = discord.Embed(title="New Team Registered", color=0x00ffcc)
    embed.add_field(name="Team Name", value=team_name, inline=False)
    embed.add_field(name="Player", value=ctx.author.mention, inline=False)
    embed.set_image(url=logo.url)
    await channel.send(embed=embed)

    await ctx.send("Team registered successfully!")

@tasks.loop(minutes=1)
async def check_registration_time():
    now = datetime.datetime.now().time()
    if now == REGISTRATION_END:
        for guild in bot.guilds:
            role = discord.utils.get(guild.roles, name=REGISTERED_ROLE)
            if role:
                for member in role.members:
                    await member.remove_roles(role)
                print("Cleared registered roles after 2:00 PM.")
