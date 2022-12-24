import discord
from discord.ext import commands

import chess
import chess.svg
import json
from cairosvg import svg2png


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialiseert de Chess command.

        Args:
            bot: Het bot object aangemaakt door commands.Bot

        Returns:
            None
        """
        self.bot = bot

    @staticmethod
    def load_board() -> chess.Board:
        """
        Laadt het bord uit een JSON bestand en zet het om naar een schaakbord object.

        Args:
            None
        
        Returns:
            Een schaakbord object
        
        """
        with open("games.json", "r") as f:
            # Leest het JSON bestand en zet het om in een dict
            game = json.loads(f.read())
            try:
                # Haalt de fen (https://nl.wikipedia.org/wiki/Forsyth-Edwards_Notation) uit het JSON
                # bestand en returned een board object met de huidige stelling
                fen = game["game"]
                return chess.Board(fen=fen)
            except KeyError:
                # Als er geen spel bezig is returned None
                return None
    
    @staticmethod
    def save_board(game: dict) -> None:
        """
        Slaat het bord op in een JSON bestand.

        Args:
            game: Een dictionary met de FEN notatie van het huidige bord.

        Returns:
            None
        """
        with open("games.json", "r+") as f:
            # Maakt het bestand leeg
            f.seek(0)
            f.truncate()
            # Schrijft de JSON string naar een JSON bestand
            f.write(json.dumps(game))
        return

    async def makemove(self, channel: discord.Message.channel, board: chess.Board, move: str) -> bool:
        """
        Doet een zet op het schaakbord en slaat het bord op.

        Args:
            channel: De Discord channel waar de zet in gedaan is.
            board: Het schaakbord object.
            move: De zet.

        Returns:
            True als de zet legaal is, False als de zet niet legaal is.
        """
        try:
            # Probeert de zet te doen
            zet = board.push_san(move)
        except ValueError as e:
            # Als de zet niet legaal is zeg dat de zet niet geldig is
            await channel.send(f"{move} is geen geldige zet. Gebruik .zetten voor een lijst van alle mogelijke zetten")
            return False
        # Haalt de nieuwe stelling op uit het bord in de FEN notatie en slaat het op in een dictionary
        fen = board.fen()
        game = {
            "game":fen
        }
        # Schrijft de huidige stelling naar een JSON bestand
        self.save_board(game)
        return True

    @commands.command(name="start")
    async def start(self, ctx):
        """
        Start een schaakspel als er nog geen spel actief is.

        Args:
            ctx: De context van het discord bericht. (https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context)
        """
        # Laadt het bord uit de JSON file
        board = self.load_board()
        # Checkt of er een bord is
        if board:
            # Als er een bord is, zeg dat er al een spel gestart is
            await ctx.send("Er is al een spel gestart. Bekijk het bord met .bord")
        else:
            # Als er nog geen spel is,
            # Maakt een nieuw schaakbord en slaat de stelling op in een dict
            board = chess.Board()
            fen = board.fen()
            game = {
                "game":fen
            }
            # Schrijft de huidige stelling naar een JSON bestand
            self.save_board(game)
            await ctx.send(f"Er is een nieuw spel gestart! Succes")

    @commands.command(name="zet")
    async def move(self, ctx, move: str):
        """
        Doet een zet aan de hand van de SAN notatie. e4 staat voor pion op e2 naar e4. Een overzicht van de stukken.
        Loper: B
        Paard: N
        Toren: R
        Dame: Q
        Koning: K

        Args:
            ctx: De context van het discord bericht. (https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context)
            move: De zet in SAN notatie
        """
        # Laadt het bord uit de JSON file
        board = self.load_board()
        # Checkt of er een bord is
        if board:
            zet = await self.makemove(ctx.channel, board, move)
        else:
            # Als er geen spel actief is, maakt een nieuw bord
            board = chess.Board()
            zet = await self.makemove(ctx.channel, board, move)
        # Checkt of de zet legaal is
        if zet:
            # Haalt op wie er aan zet is na de zet
            turn = "Zwart" if board.turn else "Wit"
            # Haalt SVG representatie uit het bord en zet het om naar een PNG bestand
            svg = chess.svg.board(board)
            svg2png(bytestring=str(svg),write_to='board.png')
            # Stuurt een plaatje van het bord
            file = discord.File('board.png')
            await ctx.send(f"{turn} heeft {move} gezet")
            await ctx.send(file=file)
        else:
            # Als de zet niet legaal is stop het command
            return
    
    @commands.command(name="zetten")
    async def zetten(self, ctx):
        """
        Stuurt een lijst met alle legale zetten die er mogelijk zijn.

        Args:
            ctx: De context van het discord bericht. (https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context)
        """
        # Laadt het bord uit de JSON file
        board = self.load_board()
        # Genereert een lijst met SAN notatie zetten
        san_list = [board.san(move) for move in board.legal_moves]
        # Stuurt de lijst in de vorm van een lange string gescheiden door een komma 
        await ctx.send(f"```{', '.join(san_list)}```")

    @commands.command(name="bord")
    async def bord(self, ctx):
        """
        Stuurt een plaatje van het huidige bord en zegt wie er aan zet is.

        Args:
            ctx: De context van het discord bericht. (https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context)
        """
        # Laadt het bord uit de JSON file
        board = self.load_board()
        # Haalt op wie er aan zet is
        turn = "Wit" if board.turn else "Zwart"
        # Haalt SVG representatie uit het bord en zet het om naar een PNG bestand
        svg = chess.svg.board(board)
        svg2png(bytestring=str(svg),write_to='board.png')
        # Stuurt een plaatje van het bord
        file = discord.File('board.png')
        await ctx.send(file=file)
        await ctx.send(f"{turn} is aan zet")

    @commands.command(name="reset")
    async def reset(self, ctx):
        """
        Reset het bord en maakt een nieuw spel aan.

        Args:
            ctx: De context van het discord bericht. (https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Context)
        """
        # Maakt een nieuw schaakbord en slaat de stelling op in een dict
        board = chess.Board()
        fen = board.fen()
        game = {
            "game":fen
        }
        # Schrijft de huidige stelling naar een JSON bestand
        self.save_board(game)
        await ctx.send("Het bord is gereset! Wit is aan zet")
        

async def setup(bot):
    await bot.add_cog(Chess(bot))
  