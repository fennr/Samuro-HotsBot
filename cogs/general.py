""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import os
import discord
from discord import Embed
from discord.ext import commands
from utils.library import files
from utils.classes.Const import config
from utils import library

guild_ids = [845658540341592096]  # Put your server ID in this array.

class general(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, context):
        """
        - Получить информацию о боте
        """
        embed = discord.Embed(
            description="Русскоязычный бот по игре Heroes of the Storm",
            color=config.success
        )
        embed.set_author(
            name="Samuro"
        )
        embed.add_field(
            name="Автор:",
            value="fenrir#5455",
            inline=True
        )
        embed.add_field(
            name="Префикс:",
            value=f"{config.bot_prefix}",
            inline=False
        )
        embed.set_footer(
            text=f"Информация для {context.author}"
        )
        await context.send(embed=embed)

    @commands.command(name="invite")
    async def invite(self, context):
        """
        - Получить ссылку для приглашения бота на свой канал
        """
        try:
            APP_ID = os.environ.get('app_id_prod')
        except:
            APP_ID = os.environ.get('APP_ID')
        embed = discord.Embed(
            title="Приглашение на сервер",
            description=f"Для подключения Самуро перейдите по [ссылке](https://discordapp.com/oauth2/authorize?&client_id={APP_ID}&permissions=270416&scope=bot)\n"
                        f"По багам/вопросам писать: __fenrir#5455__",
            color=config.info
        )
        await context.send(embed=embed)
        await context.author.send(embed=embed)


    @commands.command(name="ping")
    async def ping(self, context):
        """
        - Проверка жив ли бот
        """
        embed = discord.Embed(
            color=config.success
        )
        embed.add_field(
            name="Pong!",
            value=":ping_pong:",
            inline=True
        )
        embed.set_footer(
            text=f"Pong request by {context.author}"
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
            color=config.success
        )
        embed.set_footer(
            text=f"Опрос создан: {context.message.author} • Проголосовать!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member):
        user_avatar = library.avatar(ctx, member)
        embed = Embed(
            title=f"{member.name}",
            color=config.info

        )
        embed.set_image(
            url=user_avatar
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(general(bot))
