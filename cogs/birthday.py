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
        # Create a task to run the birthday_check method in a loop
        self.task = self.bot.loop.create_task(self.birthday_check())

    @staticmethod
    def write_json(file_name, data):
        """Write data to a JSON file"""
        with open(file_name, "r+") as f:
            # Reset file to empty
            f.seek(0)
            f.truncate()
            # Write data to file as a JSON string
            f.write(json.dumps(data))

    @staticmethod
    def read_json(file_name):
        """Read data from a JSON file"""
        with open(file_name, "r") as f:
            # Read data from file and parse as JSON
            data = json.loads(f.read())
        return data

    @staticmethod
    def get_user(data, user_id):
        """Retrieve a user from data based on their user_id"""
        for gebruiker in data["verjaardagen"]:
            if str(user_id) == str(gebruiker["user_id"]):
                return gebruiker
        # Return None if user not found
        return None
    
    async def birthday_check(self):
        # Set the task to run every day at midnight
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.now()
            # Check if it is midnight
            if now.hour == 12 and now.minute == 15:
                # Read the data from the JSON file
                data = self.read_json("verjaardagen.json")
                # Iterate through the list of users
                for user in data["verjaardagen"]:
                    # Check if the user has a birthday today
                    if user["birthday"] == now.strftime("%d-%m"):
                        # Find the user's Discord account
                        discord_user = await self.bot.fetch_user(user["user_id"])
                        # Send a birthday message to the user
                        channel = self.bot.get_channel(811527697389453332)
                        await channel.send(f"Gefeliciteerd met je verjaardag, {discord_user.mention}!")
            # Wait for one minute before checking again
            await asyncio.sleep(60)

    @commands.group(name = "birthday", invoke_without_command=True)
    async def birthday(self, ctx): 
        # This command is a group command, meaning it can have subcommands
        # If the user doesn't specify a subcommand, this function will be called
        # It sends a message to the channel with instructions on how to add a birthday
        await ctx.send("Voeg een verjaardag toe met `.birthday add @user 31-12`")
    
    @birthday.command(name="add")
    async def add(self, ctx, user: discord.Member, datum):
        """Add a birthday to the database"""
        try:
            # Read data from JSON file
            data = self.read_json("verjaardagen.json")
            # Check if user already exists in the database
            if self.get_user(data, str(user.id)):
                await ctx.send("De gebruiker staat al in de database lol")
                return
            # Create a dictionary for the new birthday
            verjaardag = {"user_id": user.id, "name":user.name, "birthday": datum}
            # Add the birthday to the database
            data["verjaardagen"].append(verjaardag)
            # Write the updated data to the JSON file
            self.write_json("verjaardagen.json", data)
            await ctx.send(f"{user.name} is toegevoegd. Goedzo")
        except (KeyError, ValueError) as e:
            # Print any key or value errors and send a message
            print(str(e))
            await ctx.send("Waarschijnlijk heb je een verkeerd format gebruikt. `.birthday add @user 31-12`")
            return
        except:
            # Print any other errors and send a message
            print(traceback.format_exc())
            await ctx.send("Fuck you Tom")
        
    @birthday.command(name="remove")
    async def remove(self, ctx, user: discord.Member):
        """Remove a birthday from the database"""
        try:
            # Read data from JSON file
            data = self.read_json("verjaardagen.json")
            for index, gebruiker in enumerate(data["verjaardagen"]):
                # Find the user in the database by their user_id
                if str(gebruiker["user_id"]) == str(user.id):
                    # Remove the user from the database
                    data["verjaardagen"].pop(int(index))
                    # Write the updated data to the JSON file
                    self.write_json("verjaardagen.json", data)
                    await ctx.send(f"{user.name} is verwijderd uit de database")   
                    return
            # If user is not found in the database, send a message
            await ctx.send("Deze gebruiker staat er niet in nie") 
        except Exception as e:
            # Print any errors and send a message
            print(traceback.format_exc())
            await ctx.send(f'Er is "iets" fout gegaan. Roep Hans maar en laat dit zien `{str(e)}`')

    @birthday.command(name="edit")
    async def edit(self, ctx, user: discord.Member, datum: str):
        """Edit a user's birthday in the database"""
        try:
            # Read data from JSON file
            data = self.read_json("verjaardagen.json")
            # Find the user in the database by their user_id
            gebruiker = self.get_user(data, str(user.id))
            if gebruiker:
                # Save the user's old birthday
                old_date = gebruiker["birthday"]
                # Update the user's birthday
                gebruiker["birthday"] = datum
                # Write the updated data to the JSON file
                self.write_json("verjaardagen.json", data)
                # Send a message with the old and new birthdays
                await ctx.send(f"Geboortedatum van {user.name} veranderd van {old_date} naar {datum}")
        except Exception as e:
            # Print any errors and send a message
            print(traceback.format_exc())
            await ctx.send(f'Er is "iets" fout gegaan. Roep Hans maar en laat dit zien `{str(e)}`')

    @birthday.command(name="view")
    async def view(self, ctx, user:discord.Member):
        try:
            # Read the data from the JSON file
            data = self.read_json("verjaardagen.json")
            # Retrieve the user object from the data
            user_obj = self.get_user(data, str(user.id))

            if user_obj:
                # Send the user's birthday to the channel
                await ctx.send(f"{user.name}'s verjaardag is op {user_obj['birthday']}")
            else:
                # Inform the user if the user is not in the data
                await ctx.send("Deze gebruiker staat niet in de database")
        except Exception as e:
            # Print the traceback and inform the user if an error occurred
            print(traceback.format_exc())
            await ctx.send(f'Er is "iets" fout gegaan. Roep Hans maar en laat dit zien `{str(e)}`')

    @birthday.command(name="list")
    async def list(self, ctx):
        try:
            data = self.read_json("verjaardagen.json")
            birthday_list = [f"{gebruiker['name']} is jarig op {gebruiker['birthday']}" for gebruiker in data["verjaardagen"]]
            
            await ctx.send("\n".join(birthday_list))
        except Exception as e:
            # Print the traceback and inform the user if an error occurred
            print(traceback.format_exc())
            await ctx.send(f'Er is "iets" fout gegaan. Roep Hans maar en laat dit zien `{str(e)}`')


async def setup(bot):
  await bot.add_cog(Birthday(bot))
  