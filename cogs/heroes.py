""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import inspect
from discord.ext import commands
from discord import Embed

from utils.library.hots import find_more_heroes, get_hero, get_master_opinion
from utils.library.embeds import add_thumbnail
from utils.hots.heroes import builds, heroes_description_short
from utils.hots.skills import skills
from utils.hots.talents import talents
from utils.classes.Hero import Hero
from utils.library import files
from utils import exceptions, log
from utils.classes.Const import config


class Heroes(commands.Cog, name="Heroes"):
    """
    — Информация о героях, их способностях и талантах
    """

    def __init__(self, bot):
        self.bot = bot

    guild_ids = [845658540341592096]  # Put your server ID in this array.

    @commands.command(name="hero")
    async def hots_hero(self, ctx, *hero_name):
        """
        - Описание героя
        """
        if len(hero_name) == 0:
            param = inspect.Parameter(name="hero_name", kind=inspect.Parameter.VAR_POSITIONAL)
            raise commands.MissingRequiredArgument(param)
        name = ' '.join(hero_name)
        hero = get_hero(name)
        if isinstance(hero, Hero):
            embed = heroes_description_short(hero, ctx.author)  # описание героя
            embed = get_master_opinion(ctx, hero.id, embed)     # мнение мастера
            embed = builds(hero, ctx.author, embed)             # билды
            embed = add_thumbnail(hero, embed)                  # иконка героя
        else:
            embed = find_more_heroes(hero, ctx.message.author)
        await ctx.send(embed=embed)

    @commands.command(name="skill")
    async def hots_skill(self, ctx, hero_name, btns='QWE'):
        """
        - Прочитать скиллы героя
        """
        hero = get_hero(hero_name)
        if isinstance(hero, Hero):
            embed = skills(hero=hero, author=ctx.author, types=['basic', 'heroic', 'trait'], btn_key=btns)
        else:
            embed = find_more_heroes(hero, ctx.author, 'skill')
        await ctx.send(embed=embed)


    @commands.command(name="talent")
    async def hots_talent(self, ctx, hero_name, lvl):
        """
        - Прочитать таланты героя
        """
        hero = get_hero(hero_name)
        if isinstance(hero, Hero):
            embed = talents(hero, lvl, ctx.author)
        else:
            embed = find_more_heroes(hero, ctx.author, 'talent')
        await ctx.send(embed=embed)

    @hots_hero.error
    @hots_skill.error
    @hots_talent.error
    async def heroes_handler(self, ctx, error):
        #print("Обработка ошибок heroes")
        error = getattr(error, 'original', error)        # получаем пользовательские ошибки
        print(error)
        #print(type(error))
        print(f"Сообщение вызвавшее ошибку: '{ctx.message.content}' guild {ctx.guild} by {ctx.author}")
        if isinstance(error, commands.MissingRequiredArgument):
            lvl = ':lvl:' if str(ctx.command) == 'talent' else ''
            embed = Embed(
                title="Ошибка! Введите все аргументы",
                color=config.error
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config.bot_prefix}{ctx.command} Самуро {lvl}_",
                inline=False
            )
            embed = files.add_footer(embed)
            log.error(ctx, "Неверно введены аргументы команды")
            await ctx.send(embed=embed)

        elif isinstance(error, exceptions.HeroNotFoundError):
            text = "Ошибка! Герой не найден"
            embed = Embed(
                title=text,
                color=config.error
            )
            embed = files.add_footer(embed)
            await ctx.send(embed=embed)

        elif isinstance(error, exceptions.WrongTalentLvl):
            embed = Embed(
                title="Ошибка! Выберите правильный уровень таланта",
                color=config.error
            )
            embed = files.add_footer(embed)
            await ctx.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Heroes(bot))
