import os
import os
import sys

import yaml
from discord.ext import commands

from hots.function import add_thumbnail, find_heroes
from hots.heroes import builds, hero_not_found, find_more_heroes, heroes_description_short, args_not_found
from hots.patchnotes import last_pn
from hots.skills import skills, read_skill_btn
from hots.talents import talents, wrong_talent_lvl, read_talent_lvl

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata' + short_patch + '.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'


class hots(commands.Cog, name="hots"):

    def __init__(self, bot):
        self.bot = bot

    guild_ids = [845658540341592096]  # Put your server ID in this array.

    @commands.command(name="patchnotes")
    async def hots_notes(self, context):
        """
        - Информация по патчноутам
        """
        embed = last_pn(None, context.author)
        await context.send(embed=embed)

    @commands.command(name="hero")
    async def hots_hero(self, context, *args):
        """
        :hero: - Описание героя, билды, разборы
        """
        hero = None
        if len(args) == 0:
            embed = args_not_found('hero')
        else:
            hero_name = ' '.join(map(str, args))  # для имен из нескольких слов
            hero_list = find_heroes(hero_name)
            if len(hero_list) == 1:
                embed = None
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = find_more_heroes(hero_list, context.author)
            else:
                embed = hero_not_found(context.author)
            if hero is not None:
                embed = heroes_description_short(hero, context.author)
                embed = builds(hero, context.author, embed)
                embed = add_thumbnail(hero, embed)
        await context.send(embed=embed)

    @commands.command(name="skill")
    async def hots_skill(self, context, *args):
        """
        :hero: :btn: - Скиллы героя на :btn: кнопках
        """
        if len(args) == 0:
            embed = args_not_found('skill')
        else:
            hero = None
            hero_name, btn_key = read_skill_btn(args)
            hero_list = find_heroes(hero_name)
            if len(hero_list) == 1:
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = find_more_heroes(hero_list, context.author, 'skill')
            else:
                embed = hero_not_found(context.author)
            if hero is not None:
                embed = skills(hero=hero, author=context.author, types=['basic', 'heroic', 'trait'], btn_key=btn_key)
        await context.send(embed=embed)

    @commands.command(name="talent")
    async def hots_talent(self, context, *args):
        """
        :hero: :lvl: - Таланты героя :lvl: уровня
        """
        if len(args) < 2:
            embed = args_not_found('talent', ':lvl:')
        else:
            hero = None
            hero_name, lvl = read_talent_lvl(args)
            hero_list = find_heroes(hero_name)
            if len(hero_list) == 1:
                embed = None
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = find_more_heroes(hero_list, context.author, 'talent', ':lvl:')
            else:
                embed = hero_not_found(context.author)
            if hero is not None:
                try:
                    embed = talents(hero, lvl, context.author)
                except:
                    embed = wrong_talent_lvl(context.author)
        await context.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(hots(bot))
