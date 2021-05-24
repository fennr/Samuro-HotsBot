import json
import os
import platform
import random
import sys

import aiohttp
import discord
import yaml
from discord.ext import commands

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class general(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, context):
        """
        Получить информацию о боте
        """
        embed = discord.Embed(
            description="Бот для хотсеров",
            color=config["success"]
        )
        embed.set_author(
            name="Mr Propper"
        )
        embed.add_field(
            name="Автор:",
            value="fenrir#5455",
            inline=True
        )
        embed.add_field(
            name="Префикс:",
            value=f"{config['bot_prefix']}",
            inline=False
        )
        embed.set_footer(
            text=f"Информация для {context.message.author}"
        )
        await context.send(embed=embed)


    @commands.command(name="ping")
    async def ping(self, context):
        """
        Проверка жив ли бот
        """
        embed = discord.Embed(
            color=config["success"]
        )
        embed.add_field(
            name="Pong!",
            value=":ping_pong:",
            inline=True
        )
        embed.set_footer(
            text=f"Pong request by {context.message.author}"
        )
        await context.send(embed=embed)

    @commands.command(name="poll")
    async def poll(self, context, *args):
        """
        Создать опрос
        """
        poll_title = " ".join(args)
        embed = discord.Embed(
            title=f"{poll_title}",
            #description=f"{poll_title}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"Опрос создан: {context.message.author} • Проголосовать!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(name="8ball")
    async def eight_ball(self, context, *args):
        """
        Спроси бота о чем угодно
        """
        answers = ['Несомненно', 'Совершенно верно', 'Без сомнения',
                   'Да - определенно', 'Насколько я понимаю, да', 'Скорее всего', 'Да',
                   'Знаки говорят да', 'Ответ в тумане, спроси еще раз', 'Спроси еще раз позднее', 'Лучше я не буду говорить',
                   'Не могу сейчас сказать', 'Сконцентрируйся и спроси позже', 'Не расчитывай на это', 'Мой ответ нет',
                   'Мои источники говорят нет', 'Прогнозы не очень хорошие', 'Очень сомнительно']
        embed = discord.Embed(
            #title="**Мой ответ:**",
            title=f"{answers[random.randint(0, len(answers))]}", #description
            color=config["success"]
        )
        embed.set_footer(
            text=f"Ответ для: {context.message.author}"
        )
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(general(bot))
