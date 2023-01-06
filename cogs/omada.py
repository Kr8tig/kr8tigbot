import discord
from discord.ext import commands
import asyncio

import requests
import json
from datetime import datetime, timedelta
import traceback

statussen = {
    "0": "Disconnected",
    "1": "Disconnected(Migrating)",
    "10": "Provisioning",
    "11": "Configuring",
    "12": "Upgrading",
    "13": "Rebooting",
    "14": "Connected",
    "15": "Connected(Wireless)",
    "16": "Connected(Migrating)",
    "17": "Connected(Wireless,Migrating)",
    "20": "Pending",
    "21": "Pending(Wireless)",
    "22": "Adopting",
    "23": "Adopting(Wireless)",
    "24": "Adopt Failed",
    "25": "Adopt Failed(Wireless)",
    "26": "Managed By Others",
    "27": "Managed By Others(Wireless)",
    "30": "Heartbeat Missed",
    "31": "Heartbeat Missed(Wireless)",
    "32": "Heartbeat Missed(Migrating)",
    "33": "Heartbeat Missed(Wireless,Migrating)",
    "40": "Isolated",
    "41": "Isolated(Migrating)"
}

status_kleuren = {
    "0": 0xf91010,
    "1": 0xf91010,
    "10": 0x10bff9,
    "11": 0x10bff9,
    "12": 0xf9da10,
    "13": 0xf9da10,
    "14": 0x10f962,
    "15": 0x10f962,
    "16": 0x10f962,
    "17": 0x10f962,
    "20": 0xf9da10,
    "21": 0xf9da10,
    "22": 0x10bff9,
    "23": 0x10bff9,
    "24": 0xf91010,
    "25": 0xf91010,
    "26": 0x10f962,
    "27": 0x10f962,
    "30": 0xf98c10,
    "31": 0xf98c10,
    "32": 0xf98c10,
    "33": 0xf98c10,
    "40": 0x10f962,
    "41": 0x10f962
}

class Omada(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = {"login": {"username": "Stijn", "password": ""},"token": None}
        self.session = requests.Session()
        self.task = self.bot.loop.create_task(self.refresh_switches())
        self.task2 = self.bot.loop.create_task(self.refresh_aps())
        self.task3 = self.bot.loop.create_task(self.refresh_dashboard())

    def login(self):
        login = "https://192.168.1.13:443/d207a34fe6b84f6ed841559fe0bb18de/api/v2/login"
        request = self.session.post(login, json=self.config["login"], verify=False)
        self.config["token"] = request.json()["result"]["token"]
        return request

    def bytes_to_gigabytes(self, b):
        gigabytes = b / (1024 ** 3)
        return int(gigabytes)
    
    async def refresh_aps(self):
        await self.bot.wait_until_ready()
        channelid = 1060883661345533982
        channel = self.bot.get_channel(channelid)
        
        with open("wireless.json", "r") as f:
            data = json.loads(f.read())

        messages = [await channel.fetch_message(message["message_id"]) for message in data["aps"]]

        emb1 = messages[0]
        emb2 = messages[1]
        emb3 = messages[2]
        emb4 = messages[3]
        emb5 = messages[4]
        emb6 = messages[5]

        while not self.bot.is_closed():
            url = "https://192.168.1.13/d207a34fe6b84f6ed841559fe0bb18de/api/v2/sites/6261406f63760347ae9a4a57/devices"
            try:
                r = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
                r.json()
                print("Valid token found!")
            except Exception as e:
                print("No valid token found...logging in!")
                self.login()
                r = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
            try:
                aps = [device for device in r.json()['result'] if device["type"] == 'ap']
                ap_1 = aps[0]
                ap_2 = aps[1]
                ap_3 = aps[2]
                ap_4 = aps[3]
                ap_5 = aps[4]
                ap_6 = aps[5]
                timestr = datetime.now() + timedelta(hours=1)

                embed_1=discord.Embed(title="AP-ICT", description=f"{statussen[str(ap_1['status'])]}", color=status_kleuren[str(ap_1['status'])])
                embed_1.add_field(name="IP", value=f"{ap_1['ip']}", inline=False)
                embed_1.add_field(name="Clients verbonden", value=f"{ap_1['clientNum']}", inline=False)
                embed_1.add_field(name="Firmware versie", value=f"{ap_1['version']} {'*update beschikbaar*' if ap_1['needUpgrade'] else ''}", inline=False)
                embed_1.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

                embed_2=discord.Embed(title="AP-VISSENKOM", description=f"{statussen[str(ap_2['status'])]}", color=status_kleuren[str(ap_2['status'])])
                embed_2.add_field(name="IP", value=f"{ap_2['ip']}", inline=False)
                embed_2.add_field(name="Clients verbonden", value=f"{ap_2['clientNum']}", inline=False)
                embed_2.add_field(name="Firmware versie", value=f"{ap_2['version']} {'*update beschikbaar*' if ap_2['needUpgrade'] else ''}", inline=False)
                embed_2.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

                embed_3=discord.Embed(title="AP-KANTOOR", description=f"{statussen[str(ap_3['status'])]}", color=status_kleuren[str(ap_3['status'])])
                embed_3.add_field(name="IP", value=f"{ap_3['ip']}", inline=False)
                embed_3.add_field(name="Clients verbonden", value=f"{ap_3['clientNum']}", inline=False)
                embed_3.add_field(name="Firmware versie", value=f"{ap_3['version']} {'*update beschikbaar*' if ap_3['needUpgrade'] else ''}", inline=False)
                embed_3.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

                embed_4=discord.Embed(title="AP-WERKPLAATS", description=f"{statussen[str(ap_4['status'])]}", color=status_kleuren[str(ap_4['status'])])
                embed_4.add_field(name="IP", value=f"{ap_4['ip']}", inline=False)
                embed_4.add_field(name="Clients verbonden", value=f"{ap_4['clientNum']}", inline=False)
                embed_4.add_field(name="Firmware versie", value=f"{ap_4['version']} {'*update beschikbaar*' if ap_4['needUpgrade'] else ''}", inline=False)
                embed_4.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

                embed_5=discord.Embed(title="AP-KANTOOR/SERVER", description=f"{statussen[str(ap_5['status'])]}", color=status_kleuren[str(ap_5['status'])])
                embed_5.add_field(name="IP", value=f"{ap_5['ip']}", inline=False)
                embed_5.add_field(name="Clients verbonden", value=f"{ap_5['clientNum']}", inline=False)
                embed_5.add_field(name="Firmware versie", value=f"{ap_5['version']} {'*update beschikbaar*' if ap_5['needUpgrade'] else ''}", inline=False)
                embed_5.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

                embed_6=discord.Embed(title="AP-BAKKERIJ", description=f"{statussen[str(ap_6['status'])]}", color=status_kleuren[str(ap_6['status'])])
                embed_6.add_field(name="IP", value=f"{ap_6['ip']}", inline=False)
                embed_6.add_field(name="Clients verbonden", value=f"{ap_6['clientNum']}", inline=False)
                embed_6.add_field(name="Firmware versie", value=f"{ap_6['version']} {'*update beschikbaar*' if ap_6['needUpgrade'] else ''}", inline=False)
                embed_6.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

                await emb1.edit(embed=embed_1)
                await emb2.edit(embed=embed_2)
                await emb3.edit(embed=embed_3)
                await emb4.edit(embed=embed_4)
                await emb5.edit(embed=embed_5)
                await emb6.edit(embed=embed_6)
            except Exception as e:
                print(traceback.format_exc())
            await asyncio.sleep(120)

    async def refresh_switches(self):
        await self.bot.wait_until_ready()
        channelid = 1060204171703353444
        channel = self.bot.get_channel(channelid)
        
        with open("network.json", "r") as f:
            data = json.loads(f.read())

        messages = [await channel.fetch_message(message["message_id"]) for message in data["switches"]]
        print(messages)
        emb1 = messages[0]
        emb2 = messages[1]
        emb3 = messages[2]

        while not self.bot.is_closed():
            url = "https://192.168.1.13/d207a34fe6b84f6ed841559fe0bb18de/api/v2/sites/6261406f63760347ae9a4a57/devices"
            try:
                r = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
                r.json()
                print("Valid token found!")
            except Exception as e:
                print("No valid token found...logging in!")
                self.login()
                r = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
            try:
                switch_1 = r.json()["result"][1]
                switch_2 = r.json()["result"][0]
                switch_3 = r.json()["result"][2]
                timestr = datetime.now() + timedelta(hours=1)
            
                embed_1=discord.Embed(title="Switch 1 (Keuken/Bakker)", description=f"{statussen[str(switch_1['status'])]}", color=status_kleuren[str(switch_1['status'])])
                embed_1.add_field(name="IP", value=f"{switch_1['ip']}", inline=False)
                embed_1.add_field(name="Clients verbonden", value=f"{switch_1['clientNum']}", inline=False)
                embed_1.add_field(name="Firmware versie", value=f"{switch_1['version']} {'*update beschikbaar*' if switch_1['needUpgrade'] else ''}", inline=False)
                embed_1.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M:%S')}")

                embed_2=discord.Embed(title="Switch 2 (ICT)", description=f"{statussen[str(switch_2['status'])]}", color=status_kleuren[str(switch_2['status'])])
                embed_2.add_field(name="IP", value=f"{switch_2['ip']}", inline=False)
                embed_2.add_field(name="Clients verbonden", value=f"{switch_2['clientNum']}", inline=False)
                embed_2.add_field(name="Firmware versie", value=f"{switch_2['version']} {'*update beschikbaar*' if switch_2['needUpgrade'] else ''}", inline=False)
                embed_2.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M:%S')}")

                embed_3=discord.Embed(title="Switch 3 (Kantoor)", description=f"{statussen[str(switch_3['status'])]}", color=status_kleuren[str(switch_3['status'])])
                embed_3.add_field(name="IP", value=f"{switch_3['ip']}", inline=False)
                embed_3.add_field(name="Clients verbonden", value=f"{switch_3['clientNum']}", inline=False)
                embed_3.add_field(name="Firmware versie", value=f"{switch_3['version']} {'*update beschikbaar*' if switch_3['needUpgrade'] else ''}", inline=False)
                embed_3.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M:%S')}")

                await emb1.edit(embed=embed_1)
                await emb2.edit(embed=embed_2)
                await emb3.edit(embed=embed_3)
            except Exception as e:
                print(traceback.format_exc())
            await asyncio.sleep(60)

    async def refresh_dashboard(self):
        await self.bot.wait_until_ready()
        channelid = 1060909275502886912
        channel = self.bot.get_channel(channelid)
        
        with open("dashboard.json", "r") as f:
            data = json.loads(f.read())

        emb = await channel.fetch_message(data["message_id"])
    

        while not self.bot.is_closed():
            url = "https://192.168.1.13/d207a34fe6b84f6ed841559fe0bb18de/api/v2/sites/6261406f63760347ae9a4a57/dashboard/overviewDiagram"
            try:
                r = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
                r.json()
                print("Valid token found!")
            except Exception as e:
                print("No valid token found...logging in!")
                self.login()
                r = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
            try:
                dashboard = r.json()["result"]
                timestr = datetime.now() + timedelta(hours=1)
            
                embed=discord.Embed(title="Dashboard", description="Kr8tig Internet", color=0xbd4e05)
                embed.add_field(name="Wired clients", value=f"{str(dashboard['wiredClientNum'])}", inline=True)
                embed.add_field(name="Wireless clients", value=f"{str(dashboard['wirelessClientNum'])}", inline=True)
                embed.add_field(name="Total clients", value=f"{str(dashboard['totalClientNum'])}", inline=True)
                embed.add_field(name="Netwerk gebruik", value=f"{str(dashboard['netUtilization'])}%", inline=True)
                embed.add_field(name="Internet snelheid", value=f"{str(dashboard['netCapacity'])} Mbps", inline=True)
                embed.add_field(name="Gateways", value=f"{str(dashboard['totalGatewayNum'])}", inline=True)
                embed.add_field(name="Connected APs", value=f"{str(dashboard['connectedApNum'])}", inline=True)
                embed.add_field(name="Connected switches", value=f"{str(dashboard['connectedSwitchNum'])}", inline=True)
                embed.add_field(name="Availabe Ports", value=f"{str(dashboard['availablePorts'])}", inline=True)
                embed.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M:%S')}")

                await emb.edit(embed=embed)

            except Exception as e:
                print(traceback.format_exc())
            await asyncio.sleep(180)

    @commands.command(name="loggedin")
    async def _logged_in(self, ctx):
        url = "https://192.168.1.13:443/d207a34fe6b84f6ed841559fe0bb18de/api/v2/loginStatus"
        request = self.session.get(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
        request.raise_for_status()
        try:
            data = request.json()
            await ctx.send(f"Hopelijk kan je hier iets uit halen: {data}")
        except Exception as e:
            await ctx.send(f"{str(e)}")
        

    @commands.command(name="login")
    async def _login(self, ctx):
        request = self.login()
        await ctx.send(f"gedaan denk ik hoop ik...weet ik veel heb je hier iets aan?{request.json()}")

    @commands.command(name="switches")
    async def switches(self, ctx):
        timestr = datetime.now() + timedelta(hours=1)

        embed_1=discord.Embed(title="Switch 1", description=f"Ophalen...")
        embed_1.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_2=discord.Embed(title="Switch 2", description=f"Ophalen...")
        embed_2.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_3=discord.Embed(title="Switch 3", description=f"Ophalen...")
        embed_3.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        emb1 = await ctx.send(embed=embed_1)
        emb2 = await ctx.send(embed=embed_2)
        emb3 = await ctx.send(embed=embed_3)
        print(emb1.id)
        with open("network.json", "r+") as f:
            data = json.loads(f.read())
            
            data["switches"][0]["message_id"] = emb1.id
            data["switches"][1]["message_id"] = emb2.id
            data["switches"][2]["message_id"] = emb3.id
            print(data)
            f.seek(0)
            f.truncate()
            f.write(json.dumps(data))

    @commands.command(name="aps")
    async def aps(self, ctx):
        timestr = datetime.now() + timedelta(hours=1)

        embed_1=discord.Embed(title="AP-ICT", description=f"Ophalen...")
        embed_1.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_2=discord.Embed(title="AP-VISSENKOM", description=f"Ophalen...")
        embed_2.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_3=discord.Embed(title="AP-KANTOOR", description=f"Ophalen...")
        embed_3.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_4=discord.Embed(title="AP-WERKPLAATS", description=f"Ophalen...")
        embed_4.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_5=discord.Embed(title="AP-KANTOOR/SERVER", description=f"Ophalen...")
        embed_5.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        embed_6=discord.Embed(title="AP-BAKKERIJ", description=f"Ophalen...")
        embed_6.set_footer(text=f"bijgewerkt om: {timestr.strftime('%H:%M')}")

        emb1 = await ctx.send(embed=embed_1)
        emb2 = await ctx.send(embed=embed_2)
        emb3 = await ctx.send(embed=embed_3)
        emb4 = await ctx.send(embed=embed_4)
        emb5 = await ctx.send(embed=embed_5)
        emb6 = await ctx.send(embed=embed_6)

        with open("wireless.json", "r+") as f:
            data = json.loads(f.read())
            
            data["aps"][0]["message_id"] = emb1.id
            data["aps"][1]["message_id"] = emb2.id
            data["aps"][2]["message_id"] = emb3.id
            data["aps"][3]["message_id"] = emb4.id
            data["aps"][4]["message_id"] = emb5.id
            data["aps"][5]["message_id"] = emb6.id
            
            f.seek(0)
            f.truncate()

            f.write(json.dumps(data))
    
    @commands.command(name="dashboard")
    async def dashboard(self, ctx):
        embed=discord.Embed(title="Dashboard", description="Kr8tig Internet", color=0xbd4e05)

        emb1 = await ctx.send(embed=embed)

        with open("dashboard.json", "r+") as f:
            data = json.loads(f.read())
            
            data["message_id"] = emb1.id
            f.seek(0)
            f.truncate()

            f.write(json.dumps(data))

    # @commands.command(name="update")
    # async def _update(self, ctx):
    #     url = "https://192.168.1.13/d207a34fe6b84f6ed841559fe0bb18de/api/v2/sites/6261406f63760347ae9a4a57/cmd/devices/00-5F-67-B4-80-34/onlineUpgrade"
    #     request = self.session.post(url, headers={"Content-Type":"application/json","Csrf-token": self.config["token"]}, verify=False)
    #     await ctx.send("Gelukt hoop ik")

    @commands.command(name="loops")
    async def loops(self, ctx):
        try:
            for task in self.bot.Task.all_tasks():
                print(task)
        except Exception as e:
            await ctx.send(str(e))


async def setup(bot):
    await bot.add_cog(Omada(bot))