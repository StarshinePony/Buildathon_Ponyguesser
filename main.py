from modules.ponyguesser import guesser
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")
authserver = os.getenv("authserver")
developer = os.getenv("developerid")
intents = discord.Intents.all()
currentprefix = 'v!'
bot = commands.Bot(command_prefix=currentprefix, intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    await bot.add_cog(guesser(bot))
    await bot.tree.sync(guild=discord.Object(id=authserver))
    await bot.tree.sync()
    print(f"Synced commands")
    print("[MAIN INFO] Bot is ready!")

@bot.tree.context_menu(name="whothis")
async def whothis(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"{member.name}", description=f" {member.id}")
    embed.add_field(name="Joined Discord", value=member.created_at.strftime("%d/%m/%Y/%H:%M:%S"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.mention for role in member.roles]), inline=False)
    embed.add_field(name="Badges", value=", ".join([badge.name for badge in member.public_flags.all()]), inline=False)
    embed.add_field(name="Activity", value=member.activity, inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)
        return
    await bot.process_commands(message)
bot.run(DISCORD_TOKEN)
