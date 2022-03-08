import os
import os
import sys

import yaml
from discord.ext import commands
from discord import Embed

from hots.function import add_thumbnail, find_heroes, hero_not_found, find_more_heroes, \
    args_not_found, read_hero_from_message, get_hero, get_master_opinion
from hots.heroes import builds, heroes_description_short
from hots.patchnotes import last_pn
from hots.skills import skills, read_skill_btn
from hots.talents import talents, wrong_talent_lvl, read_talent_lvl
from hots.Hero import Hero
from helpers import sql, log, functions

config = functions.get_config()

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata' + short_patch + '.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'


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
        — Описание героя
        """
        name = ' '.join(hero_name)
        if name is not None:
            hero = get_hero(name)
            if isinstance(hero, Hero):
                embed = heroes_description_short(hero, ctx.author)
                embed = get_master_opinion(ctx, hero.id, embed)
                embed = builds(hero, ctx.author, embed)
                embed = add_thumbnail(hero, embed)
            else:
                embed = find_more_heroes(hero, ctx.message.author)
        else:
            embed = hero_not_found()
        await ctx.send(embed=embed)


    @commands.command(name="skill")
    async def hots_skill(self, ctx, hero_name, btns='QWE'):
        """
        — Прочитать скиллы героя
        """
        name = ' '.join(hero_name)
        if name is not None:
            hero = get_hero(hero_name)
            if isinstance(hero, Hero):
                embed = skills(hero=hero, author=ctx.author, types=['basic', 'heroic', 'trait'], btn_key=btns)
            else:
                embed = find_more_heroes(hero, ctx.author, 'skill')
        else:
            embed = hero_not_found()
        await ctx.send(embed=embed)


    @commands.command(name="talent")
    async def hots_talent(self, ctx, hero_name, lvl):
        """
        — Прочитать таланты героя
        """
        if hero_name is not None:
            hero = get_hero(hero_name)
            if isinstance(hero, Hero):
                try:
                    embed = talents(hero, lvl, ctx.author)
                except:
                    embed = wrong_talent_lvl(ctx.author)
            else:
                embed = find_more_heroes(hero, ctx.author, 'talent')
        else:
            embed = hero_not_found()
        await ctx.send(embed=embed)


    @hots_hero.error
    @hots_skill.error
    @hots_talent.error
    async def heroes_hero_handler(self, ctx, error):
        print("Обработка ошибок heroes")
        if isinstance(error, commands.MissingRequiredArgument):
            lvl = ':lvl:' if str(ctx.command) == 'talent' else ''
            embed = Embed(
                title="Ошибка! Введите все аргументы",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config['bot_prefix']}{ctx.command} Самуро {lvl}_",
                inline=False
            )
            embed.set_footer(
                text=f"{config['bot_prefix']}help для просмотра справки по командам"
                # context.message.author если использовать без slash
            )
            log.error(ctx, "Неверно введены аргументы команды")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            text = "Ошибка! Герой не найден"
            embed = Embed(
                title=text,
                color=config["error"]
            )
            embed.set_footer(
                text=f"{config['bot_prefix']}help для просмотра справки по командам"
                # context.message.author если использовать без slash
            )
            await ctx.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Heroes(bot))
