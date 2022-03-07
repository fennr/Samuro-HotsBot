import os
import sys

from discord import Embed, utils
import yaml
import random
from discord.ext import commands
from helpers import functions

config = functions.get_config()

ignore_list = [
    'slash',
    'owner',
    'news',
]


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="модерынелюди")
    async def antimoders(self, context):
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
                    ':PepeSliceU:',
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

    @commands.command(name="модерылюди")
    async def antimoders(self, context):
        """
        - Анти БУНД
        """
        messages = (':shinelave:',
                    ':hotshug:',
                    ':pat_the_lord:',
                    ':Uccutecatblush:',

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
