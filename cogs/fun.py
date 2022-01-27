import os
import sys

from discord import Embed, utils
import yaml
import random
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
        messages = ('А ты не офигел ли?',
                    'Я так не считаю',
                    'Предлагаю его забанить',
                    'Может да, может нет, а может пошел ты?',
                    'Well Yes, But Actually No',
                    ':ban:',
                    ':monknofun:',
                    ':00:',
                    'Поддерживаю! Жги модеров :fire:',

                    )
        message = random.choice(messages)
        if message[0] == ":" and message[-1:] == ":":
            for guild in self.bot.guilds:
                emoji = utils.get(guild.emojis, name=message[1:-1])
                if emoji is not None:
                    message = str(emoji)
                    break
        await context.send(message)


def setup(bot):
    bot.add_cog(Fun(bot))
