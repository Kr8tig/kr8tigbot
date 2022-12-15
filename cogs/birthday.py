import discord
from datetime import time, datetime, timedelta
import asyncio
import requests
from discord.ext import commands
from discord.ext.commands.errors import BadArgument
import random
import json
import traceback


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def write_json(file_name, data):
        with open(file_name, "r+") as f:
            f.seek(0)
            f.truncate()
            f.write(json.dumps(data))

    @staticmethod
    def read_json(file_name):
        with open(file_name, "r") as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def get_user(data, user_id):
        for gebruiker in data["verjaardagen"]:
            if str(user_id) == str(gebruiker["user_id"]):
                return gebruiker
        return None

    @commands.group(name = "birthday", invoke_without_command=True)
    async def birthday(self, ctx): 
        await ctx.send("Voeg een verjaardag toe met `.birthday add @user 01-01-1970`")

    @birthday.command(name="add")
    async def add(self, ctx, user:discord.Member, datum):
        try:
            dag, maand, jaar = datum.split("-")
            datum = datetime(day=int(dag), month=int(maand), year=int(jaar)).timestamp()
            data = self.read_json("verjaardagen.json")
            if self.get_user(data, str(user.id)):
                await ctx.send("De gebruiker staat al in de database lol")
                return
            verjaardag = {"user_id":user.id,"date":datum}
            data["verjaardagen"].append(verjaardag)
            self.write_json("verjaardagen.json", data)
            await ctx.send(f"{user.name} is toegevoegd. Goedzo")
        except (KeyError, ValueError) as e:
            print(str(e))
            await ctx.send("Waarschijnlijk heb je een verkeerd format gebruikt. `.birthday add @user 01-01-1970`")
            return
        except:
            print(traceback.format_exc())
            await ctx.send("Fuck you Tom")
        
    @birthday.command(name="remove")
    async def remove(self, ctx, user:discord.Member):
        try:
            data = self.read_json("verjaardagen.json")
            for index, gebruiker in enumerate(data["verjaardagen"]):
                print(str(user.id), str(gebruiker["user_id"]))
                if str(gebruiker["user_id"]) == str(user.id):
                    print(gebruiker)
                    data["verjaardagen"].pop(int(index))
                    self.write_json("verjaardagen.json", data)
                    await ctx.send(f"{user.name} is verwijderd uit de database")   
                    return
            await ctx.send("Deze gebruiker staat er niet in nie") 
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f'Er is "iets" fout gegaan. Roep Hans maar en laat dit zien `{str(e)}`')

    @birthday.command(name="view")
    async def view(self, ctx, user:discord.Member):
        try:
            data = self.read_json("verjaardagen.json")
            gebruiker = self.get_user(data, str(user.id))
            if gebruiker:
                bday = datetime(year=datetime.now().year, month=datetime.fromtimestamp(gebruiker["date"]).month, day=datetime.fromtimestamp(gebruiker["date"]).day)
            else:
                await ctx.send("Deze user staat er niet in nie")
                return
            if bday > datetime.now():
                new_date = bday - datetime.now()
                await ctx.send(f"{user.name} is jarig over {new_date.days} dagen en {int(new_date.seconds/60/60)} uur op {bday.day}-{bday.month}")
                return
            else:
                await ctx.send(f"{user.name} is al jarig geweest dit jaar op {bday.day}-{bday.month}")
                return
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f'Er is "iets" fout gegaan. Roep Hans maar en laat dit zien `{str(e)}`')


def setup(bot):
  bot.add_cog(Birthday(bot))
  