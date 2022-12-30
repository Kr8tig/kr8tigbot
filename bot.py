# Works with Python 3.6+
import discord
import os
import asyncio
from discord import Game
from discord.ext import commands
from discord.utils import get
import json
import sys
import random
import requests
from datetime import time, datetime, timedelta

from secret import TOKEN2


bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())


@bot.event
async def on_ready():
    # sets Playing message on discord
    await bot.change_presence(activity = discord.Activity(type=2, name= "Bring me to life by Evanescence 🖤"))
    # prints succesful launch in console
    print(f"{bot.user.name} is watching. be warned lol")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  undergod = 377515612127232011
  hans = 867378778341769247
  c = message.content
  c = c.lower()
  msgs = ["ik win", "ik heb gewonnen", "ik ben de winnaar", "ik win ook", "ik heb ook gewonnen", "ik ben ook een winnaar"]
  for L in msgs:
    if L in c:
      if message.author.id != undergod and message.author.id != hans:
        await message.channel.send("Nee, loser.")
      else:
        await message.channel.send("Ikr, jij bent zo cool.")
  await bot.process_commands(message)


@bot.command(name="meme")
async def meme(ctx):
  subreddit = "memes"
  channel = bot.get_channel(893402532154605598)

  # Set the URL for the Reddit API
  url = f"https://www.reddit.com/r/{subreddit}/random.json"

  # Send a request to the Reddit API to get a random post from the subreddit
  response = requests.get(url, headers={"User-Agent": "MemeFetcherBot/1.0"})

  # Get the data for the random post
  data = response.json()[0]["data"]["children"][0]["data"]

  # Send the random meme to the Discord channel
  await channel.send(data["url"])


@bot.command(name = "load")
@commands.has_permissions(administrator=True)
async def load(ctx, cog):
  await bot.load_extension(f"cogs.{cog}")
  await ctx.channel.send(f"hey look, {cog} is back! i have nothing to do with it disappearing, trust me.")


@bot.command(name = "unload")
@commands.has_permissions(administrator=True)
async def unload(ctx, cog):
  await bot.unload_extension(f"cogs.{cog}")
  await ctx.channel.send(f"{cog} has been unloaded, didnt like it anyways.")


@bot.command(name = "reload")
@commands.has_permissions(administrator=True)
async def reload(ctx, cog):
  await bot.unload_extension(f"cogs.{cog}")
  await bot.load_extension(f"cogs.{cog}")
  funi = random.choices([f"Reloaded cog: {cog}", f"eh so i think i just deleted {cog}... but hey, now you have something new to do!"], weights=(98, 2))
  await ctx.channel.send(funi[0])


async def load_cogs():
  for L in os.listdir("./cogs"):
    if L.endswith(".py") and L != "__init__.py":
      await bot.load_extension(f"cogs.{L[:-3]}")


async def main():
  async with bot:
    await load_cogs()
    await bot.start(TOKEN2)


asyncio.run(main())
