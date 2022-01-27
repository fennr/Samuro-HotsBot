import os
import sys

from discord import Embed
import yaml
from discord.ext import commands

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

ignore_list = [
    'slash',
    'owner',
    'news',
]

class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="модерынелюди")
    async def moders(self, context):
        """
        - БУНД
        """
        message = "Поддерживаю! Жги модеров :fire:"
        await context.send(content=message)


def setup(bot):
    bot.add_cog(Fun(bot))
