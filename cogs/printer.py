import discord
from datetime import time, datetime, timedelta
import asyncio
import requests
from discord.ext import commands
from discord.ext.commands.errors import BadArgument
import random


class PrinterDied(Exception):
    def __init__(self, message = "I suggest you turn the printer on first, it generally works better that way.") -> None:
        self.message = message
        super().__init__(self.message)


class PrinterAPI:

    base_url = "http://192.168.1.14/api/{}?apikey={}"

    def __init__(self, api_key) -> None:
        """
        Maakt verbinding met de OctoPrint API en geeft standaard functionaliteit.

        Arguments:
            api_key: Een authenticatie key verkregen door de OctoPrint Web interface.

        Returns:
            None
        """
        self.api_key = api_key
        self.session = requests.Session()

    def _url_builder(self, feature: str) -> str:
        """
        Maakt de URL gebaseerd op welke functionaliteit de gebruiker nodig heeft.

        Arguments:
            feature: De functionaliteit zoals connection, printer of job

        Returns:
            De URL
        """
        url = self.base_url.format(feature, self.api_key)
        return url

    def connect(self) -> requests.Response:
        """
        Verbindt de printer met OctoPrint.

        Arguments:
            None

        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("connection")
        # Connect payload voor de request
        data = {"command": "connect"}
        # POST request met de connect payload
        response = self.session.post(url, json=data)
        return response
    
    def disconnect(self) -> requests.Response:
        """
        Verbreekt de vervinding van de printer met OctoPrint.

        Arguments:
            None

        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("connection")
        # Disconnect payload voor de request
        data = {"command": "disconnect"}
        # POST request met de disconnect payload
        response = self.session.post(url, json=data)
        return response

    def cancel(self) -> requests.Response:
        """
        Stopt de huidige print job van de 3Dprinter.

        Arguments:
            None
        
        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("job")
        # Cancel payload voor de request
        data = {"command": "cancel"}
        # POST request met de cancel payload
        response = self.session.post(url, json=data)
        return response

    def move(self, x:int=0, y:int=0, z:int=0) -> requests.Response:
        """
        Beweegt de printkop van de 3Dprinter.

        Arguments:
            x: Het X co??rdinaat van de printkop (links/rechts)
            y: Het Y co??rdinaat van de printkop (achter/voren)
            z: Het Z co??rdinaat van de printkop (boven/beneden)

        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("printer/printhead")
        # Jog payload voor de request
        data = {"command": "jog", "x":x, "y":y, "z":z}
        # POST request met de jog payload
        response = self.session.post(url, json=data)
        return response

    def home(self) -> requests.Response:
        """
        Brengt de printkop van de 3Dprinter naar de home positie.

        Arguments:
            None

        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("printer/printhead")
        # Home payload voor de request
        data = {"command": "home", "axes": ["x", "y", "z"]}  
        # POST request met de home payload  
        response = self.session.post(url, json=data)

    def heat(self, temp: int) -> requests.Response:
        """
        Verhit de printkop naar een gespecificeerde temperatuur.

        Arguments:
            temp: De gewenste temperatuur.

        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("printer/tool")
        # Target payload met temperatuur voor de request
        data = {
            "command":"target",
            "targets": {
                "tool0":int(temp)
            }
        }
        # POST request met de target payload
        response = self.session.post(url, json=data)
        return response

    def extrude(self, amount: int) -> requests.Response:
        """
        Extrude een gespecificeerd aantal fillament in milimeters.

        Arguments:
            amount: De hoeveelheid fillament in milimeters.

        Returns:
            De response van OctoPrint i.e status, error etc.
        """
        url = self._url_builder("printer/tool")
        # Extrude payload voor de request
        data = {
            "command":"extrude",
            "amount": int(amount)
        }
        # POST request met de extrude payload
        response = self.session.post(url, json=data)
        return response

    @property
    def is_printing(self) -> bool:
        url = self._url_builder("printer")
        # GET request om de JSON op te halen met printer info
        response = self.session.get(url).json()
        try:
            # Checkt of de printer aan het printen is.
            if response["state"]["flags"]["printing"]:
                return True
            else:
                return False
        # Als de printer uit staat geef een error
        except KeyError:
            raise PrinterDied

    @property
    def status(self) -> dict:
        url = self._url_builder("connection")
        # GET request om de connectie info op te halen
        response = self.session.get(url).json()
        return response["current"]["state"]

    @property
    def printer(self) -> dict:
        url = self._url_builder("printer")
        # GET request om de printer info op te halen
        response = self.session.get(url).json()
        try:
            response["state"]
        except KeyError:
            raise PrinterDied

        return response

    @property
    def job(self) -> dict:
        url = self._url_builder("job")
        # GET request om de job info op te halen
        response = self.session.get(url).json()
        return response
    


class Printer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "1C6E30FB61474C00A2CAB8D3199B3555"
        self.p = PrinterAPI(self.api_key)
        self.task = self.bot.loop.create_task(self.is_printing_task())

    async def notify_task(self, author):
        await self.bot.wait_until_ready()
        while self.p.is_printing:
            await asyncio.sleep(10)
        await author.send("Print is klaar! :D uwu") 
    
    async def is_printing_task(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                if self.p.is_printing:
                    await self.bot.change_presence(activity = discord.Activity(type=0, name= f"OctoPrint printing: {self.p.job['job']['file']['name']} Time left:{str(timedelta(seconds = self.p.job['progress']['printTimeLeft']))}"))
                    await asyncio.sleep(10)
                    print("sleeping printing")
                else:
                    await self.bot.change_presence(activity = discord.Activity(type=2, name= "Bring me to life by Evanescence ????"))
                    await asyncio.sleep(60)
                    print("sleeping not printing")
            except PrinterDied:
                await self.bot.change_presence(activity = discord.Activity(type=2, name= "Bring me to life by Evanescence ????"))
                await asyncio.sleep(120)
                print("sleeping printer turned off")            

    @commands.command(name = "status")
    async def status(self, ctx):
        now = datetime.now() + timedelta(hours = 1)
        emb = discord.Embed(title = "*Printer Status*", description = "ehhhh eehhhhh ehmmm ehhh erhhhh euhhh ehhhm")
        
        if self.p.status != "Closed":
            if not self.p.printer["state"]["flags"]["printing"]:
                emb.color = 0x12cc15
                emb.add_field(name="__Status__:", value="ready :D", inline=False)
                emb.add_field(name="__Temperatuur__:", value=f"**Bed:**\n{self.p.printer['temperature']['bed']['actual']}\n\n**Printkop:**\n{self.p.printer['temperature']['tool0']['actual']}", inline=False)
                emb.set_footer(text="Copyright ?? 2022 P!ngStudios, inc. All Rights Reserved")     
            else:
                emb.color = 0xed7b09
                emb.add_field(name="__Job Info__:", value=f"**File:**\n{self.p.job['job']['file']['name']}\n\n**Start Tijd:**\n{(now - timedelta(seconds=self.p.job['progress']['printTime'])).strftime('%m/%d/%Y, %H:%M:%S')}", inline=False)
                emb.add_field(name="__Progress__:", value=f"**Totale Print Tijd:**\n{str(timedelta(seconds = (self.p.job['progress']['printTimeLeft'] + self.p.job['progress']['printTime'])))}\n\n**Print Tijd Over:**\n{str(timedelta(seconds = self.p.job['progress']['printTimeLeft']))}", inline=True)
                emb.add_field(name="__Temperatuur__:", value=f"**Bed:**\n{self.p.printer['temperature']['bed']['actual']}\n\n**Printkop:**\n{self.p.printer['temperature']['tool0']['actual']}", inline=True)
                emb.set_footer(text="Copyright ?? 2022 P!ngStudios, inc. All Rights Reserved")
        else:
            emb.color = 0xd11608
            emb.add_field(name="__Status__:", value="offline D:", inline=False)
            emb.set_footer(text="Copyright ?? 2022 P!ngStudios, inc. All Rights Reserved")
    
        await ctx.channel.send(embed=emb)

    @commands.command(name = "connect")
    @commands.has_role("Printer Operator")
    async def connect(self, ctx):
        if self.p.status != "Operational":
            self.p.connect()
            await asyncio.sleep(1)
            if self.p.status == "Operational":
                await ctx.channel.send("```\n... P R I N T E R  C O N N E C T E D ...\n```")
            else:
                await ctx.channel.send("You might wanna just turn the printer on first, that probably would help i think.")
        else:
            await ctx.channel.send("The printer is already connected, you dunce.")

    @commands.command(name = "disconnect")
    @commands.has_role("Printer Operator")
    async def disconnect(self, ctx):
        if self.p.status == "Operational":
            
            if not self.p.printer["state"]["flags"]["printing"]: 
        
                self.p.disconnect()
                await ctx.channel.send("```\n... P R I N T E R  D I S C O N N E C T E D ...\n```")
            else:
                await ctx.channel.send("Are you trying to sabotage stuff or are you just stupidly unaware?")
        
        else:
            await ctx.channel.send("The printer wasn't even connected to begin with, what are you doing?")

    @commands.command(name = "cancel")
    @commands.has_role("Printer Operator")
    async def cancel(self, ctx):
        try: 
            if self.p.printer["state"]["flags"]["printing"]:
                emb = discord.Embed(title = "Cancel Receipt", description = "You canceled a job. You menace.", color = 0xbf0a67)
                emb.add_field(name = "__Canceled File__:", value = self.p.job['job']['file']['name'], inline = False)
                emb.add_field(name = "__Time Wasted__:", value = str(timedelta(seconds = self.p.job["progress"]["printTime"])), inline = False)
                self.p.cancel()
                await ctx.channel.send(embed = emb)
                await asyncio.sleep(10)
                self.p.move(z=40)
            else:
                await ctx.channel.send("You might wanna start printing something before canceling it, would be kinda pointless otherwise.")
        except KeyError: 
            await ctx.channel.send("the printer isn't connected btw, thought you should know.")
    
    @commands.command(name = "move")
    @commands.has_role("Printer Operator")
    async def move(self, ctx, x=0, y=0, z=0):
        try:
            if not self.p.printer["state"]["flags"]["printing"]:
                
                self.p.move(x=int(x),y=int(y),z=int(abs(z)))
                await ctx.channel.send(f"Moved the print head by: ```\nleft/right: {x}\nfront/back: {y}\nup: {abs(z)}\n```")
                
        except PrinterDied as e:
            await ctx.channel.send(e.message)

    @commands.command(name = "temp")
    @commands.has_role("Printer Operator")
    async def temp(self, ctx, temp=0):
        try:
            if not self.p.printer["state"]["flags"]["printing"]:
                self.p.heat(int(temp))
                await ctx.channel.send(f"changing the temperature to {temp} degrees")
                
        except PrinterDied as e:
            await ctx.channel.send(e.message)
            
    @commands.command(name = "refill")
    @commands.has_role("Printer Operator") 
    async def refill(self, ctx):
        try:
            if not self.p.printer["state"]["flags"]["printing"]:
                await ctx.channel.send("Heating up...")
                self.p.heat(180)
                while self.p.printer["temperature"]["tool0"]["actual"] < 180:
                    await asyncio.sleep(1)
                await ctx.channel.send("De printer is klaar met verwarmen, je kan nu de fillament vervangen. stuur \"doorgaan\" als je klaar bent om het restant te extruden.")

                def check(author):
                    def inner_check(message):
                        if message.author == author and (message.content).lower() == "doorgaan":
                            return True
                        else:
                            return False
                    return inner_check
                msg = await self.bot.wait_for("message", check=check(ctx.author), timeout=300)

                if msg:
                    self.p.extrude(150)
                    await ctx.channel.send("My fillament is extruding UwU")
                    self.p.heat(0)
            else:
                await ctx.channel.send("Dude, something is being printed, you absolute psycho, fuck")

        except PrinterDied as e:
            await ctx.channel.send(e.message)        
    
    @commands.command(name = "home")
    @commands.has_role("Printer Operator")
    async def home(self, ctx):
        try:
            
            if not self.p.printer["state"]["flags"]["printing"]: 
                await ctx.channel.send("????")
                self.p.home()
            
            else:
                await ctx.channel.send("The printer in the middle of creating art, please do not disturb it any further and kindly go fuck yourself.")

        except PrinterDied as e:
            await ctx.channel.send(e.message)
    
    @commands.command(name = "notify")
    @commands.has_role("Printer Operator")
    async def notify(self, ctx):
        task = self.bot.loop.create_task(self.notify_task(ctx.author))
        await ctx.channel.send("Ik slide in je dm's als de print klaar is uwu")

    @commands.command(name = "stijn")
    async def stijn(self, ctx):
        stijnisms = ["Jongens, laten we een pijpbom maken", "Drugs????", "ReMarkt laat mij huilen", "Let's gooooooooooooo", "Gawdmotherfuckingdaymmm", "Ik zou vaker willen gaan scannen bij Remarkt :)"]
        await ctx.channel.send(random.choice(stijnisms))
    

async def setup(bot):
  await bot.add_cog(Printer(bot))
  