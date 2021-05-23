import os
import sys
import json

import yaml
import discord
from discord.ext import commands

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


def create_ru_list_heroes(filename):
    ru_heroes_list = []
    with open(filename, 'r') as heroes_txt:
        for line in heroes_txt:
            hero_ru, tail = line.split(sep='/', maxsplit=1)
            hero_en, tail = tail.split(sep=' — ', maxsplit=1)
            stlk_url, tail = tail.split(sep=' ', maxsplit=1)
            tail = tail[1:-2]
            shortbuild, hero_name = tail.split(sep=',')
            heroes = dict(name_ru=hero_ru, name_en=hero_en, name=hero_name, build=shortbuild, url=stlk_url)
            ru_heroes_list.append(heroes)

    return ru_heroes_list

def find_hero(hero_name):
    hero_name = hero_name.capitalize()
    stlk_file = 'data/stlk_builds.txt'
    heroes_list = create_ru_list_heroes(stlk_file)
    for hero in heroes_list:
        if (hero['name_ru'] == hero_name) or (hero['name'] == hero_name):
            return hero
    return None

def find_wrong_hero(hero_name):
    hero_name = hero_name.capitalize()
    stlk_file = 'data/stlk_builds.txt'
    heroes_list = create_ru_list_heroes(stlk_file)
    wrong_list = []
    for hero in heroes_list:
        if (hero['name_ru'][:3] == hero_name[:3]) or (hero['name'][:3] == hero_name[:3]) or \
        (hero['name_ru'][-3:] == hero_name[-3:]) or (hero['name'][-3:] == hero_name[-3:]):
            wrong_list.append(hero)
    return wrong_list


# Here we name the cog and create a new class for the cog.

class hots(commands.Cog, name="hots"):

    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.command(name="hero")
    async def hotshero(self, context, *args):
        """
        Информация по герою
        """
        heroesfire_url = 'https://www.heroesfire.com/hots/wiki/heroes/'
        blizzhero_url = 'https://blizzardheroes.ru/guides/'
        if len(args) == 0:
            embed = discord.Embed(
                title="После команды введите имя героя",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value="!hero Самуро",
                inline=False
            )
        else:
            hero = find_hero(args[0])
            wrong_hero_list = []
            if hero is None:
                wrong_hero_list = find_wrong_hero(args[0])
                print(wrong_hero_list)
                print(len(wrong_hero_list))
                if len(wrong_hero_list) > 1:
                    embed = discord.Embed(
                        title="Возможно вы имели в виду:",
                        color=config["warning"]
                    )
                    for wrong_hero in wrong_hero_list:
                        embed.add_field(
                            name="{} / {}".format(wrong_hero['name'], wrong_hero['name_ru']),
                            value="Билд: {} - {}".format(wrong_hero['build'], wrong_hero['url']),
                            inline=False
                        )
                    embed.set_footer(
                        text=f"Информация для {context.message.author}"
                    )
                elif len(wrong_hero_list) == 1:
                    hero = wrong_hero_list[0]
            if hero is not None:
                embed = discord.Embed(
                    title="Билды по герою:",
                    color=config["success"]
                )
                embed.set_author(
                    name='{} / {}'.format(hero['name'], hero['name_ru'])
                )
                embed.add_field(
                    name="Stalk build: {}".format(hero['build']),
                    value="{}".format(hero['url']),
                )
                embed.add_field(
                    name="Heroesfire:",
                    value="{}{}".format(heroesfire_url, hero['name']),
                    inline=False
                )
                embed.add_field(
                    name="blizzhero:",
                    value="{}{}".format(blizzhero_url, hero['name']),
                    inline=False
                )
                embed.set_footer(
                    text=f"Информация для {context.message.author}"
                )
            elif len(wrong_hero_list) == 0:
                embed = discord.Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )

        await context.send(embed=embed)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(hots(bot))
