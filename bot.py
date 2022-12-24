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

from secret import TOKEN


bot = commands.Bot(command_prefix=".")


WHEN = time(16, 00, 0)  # 12:00 PM
channel_id = 893402532154605598 # Put your channel id here


@bot.event
async def on_ready():
    # sets Playing message on discord
    await bot.change_presence(activity = discord.Activity(type=2, name= "Bring me to life by Evanescence 🖤"))
    # prints succesful launch in console
    print(f"{bot.user.name} is watching. be warned lol")


# async def called_once_a_day():  # Fired every day
#     await bot.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
#     channel = bot.get_channel(channel_id) # Note: It's more efficient to do bot.get_guild(guild_id).get_channel(channel_id) as there's less looping involved, but just get_channel still works fine
#     deadline = datetime(2022, 10, 18, 9, 0, 0)
#     poop_time = datetime.now() + timedelta(hours = 1)
#     t = deadline - poop_time
    
#     try:
#       msg = await channel.fetch_message(channel.last_message_id)
#       if msg.author == bot.user:
#         await msg.delete()
#     except Exception as e:
#       print(e)
    
#     if t.days > 7 and poop_time.weekday() < 5:
#       await channel.send(f"hahaha jullie hebben nog maar {int(t.days/7)} weken en {int(t.days)%7} dagen voor jullie project hahahaha")
#     elif t.days == 7 and poop_time.weekday() < 5:
#       await channel.send("hahaha jullie hebben nog maar 1 week voor jullie project hahahaha")
#     elif t.days < 7 and poop_time.weekday() < 5:
#       await channel.send(f"hahaha jullie hebben nog maar {t.days} dagen voor jullie project hahahaha")


# async def background_task():
#     now = datetime.now() + timedelta(hours = 1)
#     if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
#         tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
#         seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
#         await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
#     while True:
#         now = datetime.now() + timedelta(hours = 1) # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
#         target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
#         seconds_until_target = (target_time - now).total_seconds()
#         await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
#         await called_once_a_day()  # Call the helper function that sends the message
#         tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
#         seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
#         await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration


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
    await bot.start(TOKEN)


asyncio.run(main())