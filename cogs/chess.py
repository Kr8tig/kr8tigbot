import discord
from discord.ext import commands

import chess
import chess.svg
import json
from cairosvg import svg2png


class Chess(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    def load_board(self):
        with open("games.json", "r") as f:
            game = json.loads(f.read())
            try:
                fen = game["game"]
                return chess.Board(fen=fen)
            except KeyError as e:
                return None
    
    def save_board(self, game):
        with open("games.json", "r+") as f:
            # Reset file to empty
            f.seek(0)
            f.truncate()
            # Write data to file as a JSON string
            f.write(json.dumps(game))
        return

    @commands.command(name="start")
    async def start(self, ctx):
        board = self.load_board()

        if board:
            await ctx.send("Er is al een spel gestart. Bekijk het bord met .bord")
        else:
            board = chess.Board()
            fen = board.fen()
            game = {
                "game":fen
            }
            self.save_board(game)
            await ctx.send(f"Er is een nieuw spel gestart! Succes")

    @commands.command(name="zet")
    async def move(self, ctx, move):
        board = self.load_board()

        if board:
            try:
                zet = board.push_san(move)
            except ValueError as e:
                await ctx.send(f"{move} is geen geldige zet. Gebruik .zetten voor een lijst van alle mogelijke zetten")
                return
            fen = board.fen()
            game = {
                "game":fen
            }
            self.save_board(game)
        else:
            board = chess.Board()
            board.push_san(move)
            fen = board.fen()
            game = {
                "game":fen
            }
            self.save_board(game)
        
        turn = "Zwart" if board.turn else "Wit"

        svg = chess.svg.board(board)
        svg2png(bytestring=str(svg),write_to='board.png')

        file = discord.File('board.png')
        await ctx.send(f"{turn} heeft {move} gezet")
        await ctx.send(file=file)

    @commands.command(name="turn")
    async def turn(self, ctx):
        board = self.load_board()

        if board:
            turn = "Wit" if board.turn else "Zwart"
            await ctx.send(f"{turn} is aan de beurt")
        else:
            await ctx.send("Er is geen actief bord")
    
    @commands.command(name="zetten")
    async def zetten(self, ctx):
        board = self.load_board()
        san_list = [board.san(move) for move in board.legal_moves]
        await ctx.send(f"```{', '.join(san_list)}```")

    @commands.command(name="bord")
    async def bord(self, ctx):
        board = self.load_board()

        turn = "Wit" if board.turn else "Zwart"

        svg = chess.svg.board(board)
        svg2png(bytestring=str(svg),write_to='board.png')

        file = discord.File('board.png')
        
        await ctx.send(file=file)
        await ctx.send(f"{turn} is aan zet")

    @commands.command(name="reset")
    async def reset(self, ctx):
        board = chess.Board()
        fen = board.fen()
        game = {
            "game":fen
        }
        self.save_board(game)
        await ctx.send("Het bord is gereset! Wit is aan zet")
        

def setup(bot):
    bot.add_cog(Chess(bot))
  