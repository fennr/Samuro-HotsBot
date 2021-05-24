import os
import sys
import json

import yaml
import discord
from github import Github
from urllib.request import urlopen
import re
from discord.ext import commands

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


TOKEN = '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'
g = Github(TOKEN)
repo = g.get_user().get_repo('discord-bot')

def create_ru_list_heroes(filename):
    ru_heroes_list = []
    heroes_txt = urlopen(filename.download_url).read()
    heroes_txt = heroes_txt.decode('cp1251').splitlines()
    for line in heroes_txt:
        if len(line) > 0:
            hero_ru, tail = line.split(sep='/', maxsplit=1)
            hero_en, tail = tail.split(sep=' — ', maxsplit=1)
            stlk_url, tail = tail.split(sep=' ', maxsplit=1)
            tail = tail[1:-1]
            shortbuild, hero_name = tail.split(sep=',')
            heroes = dict(name_ru=hero_ru, name_en=hero_en, name=hero_name, build=shortbuild, url=stlk_url)
            ru_heroes_list.append(heroes)

    return ru_heroes_list

def find_hero(hero_name):
    hero_name = hero_name.capitalize()
    stlk_file = repo.get_contents('data/stlk_builds.txt')
    heroes_list = create_ru_list_heroes(stlk_file)
    for hero in heroes_list:
        if (hero['name_ru'] == hero_name) or (hero['name'] == hero_name):
            return hero
    return None

def find_wrong_hero(hero_name):
    hero_name = hero_name.capitalize()
    stlk_file = repo.get_contents('data/stlk_builds.txt')
    heroes_list = create_ru_list_heroes(stlk_file)
    wrong_list = []
    for hero in heroes_list:
        if (hero['name_ru'][:3] == hero_name[:3]) or (hero['name'][:3] == hero_name[:3]) or \
        (hero['name_ru'][-3:] == hero_name[-3:]) or (hero['name'][-3:] == hero_name[-3:]):
            wrong_list.append(hero)
    return wrong_list

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return per_lvl(cleantext)

def per_lvl(raw_text):
    match = re.search('~~.{3,5}~~', raw_text)
    if match:
        cleanr = re.compile('~~.{3,5}~~')
        left, dig, right = raw_text.split('~~', maxsplit=2)
        dig = float(dig) * 100
        cleantext = re.sub(cleanr, '(+{}% за лвл)'.format(dig), raw_text)
        return cleantext
    else:
        return raw_text


# Here we name the cog and create a new class for the cog.

class hots(commands.Cog, name="hots"):

    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.command(name="hero")
    async def hots_hero(self, context, *args):
        """
        Актуальные билды для героя | указать героя
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
                if len(wrong_hero_list) > 1:
                    embed = discord.Embed(
                        title="Возможно вы имели в виду:",
                        color=config["warning"]
                    )
                    for wrong_hero in wrong_hero_list:
                        embed.add_field(
                            name="{} / {}".format(wrong_hero['name'], wrong_hero['name_ru']),
                            value="Введи: !hero {}".format(wrong_hero['name_ru']),
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

    @commands.command(name="skill")
    async def hots_skill(self, context, *args):
        """
        Информация о скиллах героя | указать героя
        """
        # json с данными по всем героям
        heroes_json_file = 'data/heroesdata.json'
        with open(heroes_json_file) as heroes_json:
            heroes_data = json.load(heroes_json)

        # json с внутриигровыми строками перевода текста
        gamestrings_json_file = 'data/gamestrings.json'
        with open(gamestrings_json_file, encoding='utf-8') as ru_json:
            ru_data = json.load(ru_json)

        if len(args) == 0:
            embed = discord.Embed(
                title="После команды введите имя героя",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value="!skill Самуро",
                inline=False
            )
        else:
            hero_list = []
            hero = find_hero(args[0])
            print(hero)
            if hero is None:
                hero_list = find_wrong_hero(args[0])
            if hero is not None or len(hero_list) == 1:
                if len(hero_list) == 1:
                    hero = hero_list[0]
                # json по отдельному герою, содержит более детальную информацию
                hero_json_file = 'hero/' + hero['name'] + '.json'
                with open(hero_json_file) as hero_json:
                    hero_data = json.load(hero_json)
                full_hero = heroes_data[hero_data['cHeroId']]
                basic_ability = full_hero['abilities']['basic']
                heroic_ability = full_hero['abilities']['heroic']
                ability = basic_ability + heroic_ability
                embed = discord.Embed(
                    title="Способности героя {}:".format(hero['name_ru']),
                    color=config["success"]
                )
                for i in range(len(ability)):  # считываем все абилки
                    # считываем файл с переводом
                    ability_name = hero_data['abilities'][hero['name']][i]['name'].replace(' ', '')
                    ability_nameID = ability[i]['nameId']
                    ability_buttonID = ability[i]['buttonId']
                    ability_hotkey = ability[i]['abilityType']
                    full_talent_name_en = ability_nameID + '|' + \
                                          ability_buttonID + '|' + ability_hotkey + '|False'
                    ability_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]

                    ability_desc = hero_data['abilities'][hero['name']][i]['description']
                    ability_desc_ru = cleanhtml(ru_data['gamestrings']['abiltalent']['full'][full_talent_name_en])
                    embed.add_field(
                        name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                        value="{}".format(ability_desc_ru),
                        inline=False
                    )
            elif len(hero_list) > 1:
                embed = discord.Embed(
                    title="Возможно вы имели в виду:",
                    color=config["warning"]
                )
                for wrong_hero in hero_list:
                    embed.add_field(
                        name="{} / {}".format(wrong_hero['name'], wrong_hero['name_ru']),
                        value="Введи: !skill {}".format(wrong_hero['name_ru']),
                        inline=False
                    )
                embed.set_footer(
                    text=f"Информация для {context.message.author}"
                )
            elif len(hero_list) == 0:
                embed = discord.Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )

        await context.send(embed=embed)

    @commands.command(name="talent")
    async def hots_talent(self, context, *args):
        """
        Информация о талантах героя | указать героя и уровень
        """
        # json с данными по всем героям
        heroes_json_file = 'data/heroesdata.json'
        with open(heroes_json_file) as heroes_json:
            heroes_data = json.load(heroes_json)

        # json с внутриигровыми строками перевода текста
        gamestrings_json_file = 'data/gamestrings.json'
        with open(gamestrings_json_file, encoding='utf-8') as ru_json:
            ru_data = json.load(ru_json)
        if len(args) < 2:
            embed = discord.Embed(
                title="После команды введите имя героя и уровень таланта",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value="!talent Самуро 13",
                inline=False
            )
        else:
            hero_list = []
            if hero is None:
                hero_list = find_wrong_hero(args[0])
            if hero is not None or len(hero_list) == 1:
                if len(hero_list) == 1:
                    hero = hero_list[0]
                # json по отдельному герою, содержит более детальную информацию
                hero_json_file = 'hero/' + hero['name'] + '.json'
                with open(hero_json_file) as hero_json:
                    hero_data = json.load(hero_json)
                full_hero = heroes_data[hero_data['cHeroId']]
                level = 'level' + args[1]
                talents = None
                try:
                    talents = full_hero['talents'][level]
                except:
                    embed = discord.Embed(
                        title="Ошибка! Выберете правильный уровень",
                        color=config["error"]
                    )
                embed = discord.Embed(
                    title="Таланты героя {} на {} уровне:".format(hero['name_ru'], args[1]),
                    color=config["success"]
                )
                if talents is not None:
                    for i in range(len(talents)):
                        talent_name = hero_data['talents'][args[1]][i]['name']
                        talent_nameID = talents[i]['nameId']
                        talent_buttonID = talents[i]['buttonId']
                        talent_hotkey = talents[i]['abilityType']
                        full_talent_name_en = talent_nameID + '|' + \
                                              talent_buttonID + '|' + talent_hotkey + '|False'
                        talent_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
                        talent_desc_ru = cleanhtml(ru_data['gamestrings']['abiltalent']['full'][full_talent_name_en])
                        embed.add_field(
                            name='{} / {} ({})'.format(talent_name, talent_name_ru, talent_hotkey),
                            value="{}".format(talent_desc_ru),
                            inline=False
                        )
                else:
                    embed = discord.Embed(
                        title="Ошибка! Выберете правильный уровень таланта",
                        color=config["error"]
                    )
            elif len(hero_list) > 1:
                embed = discord.Embed(
                    title="Возможно вы имели в виду:",
                    color=config["warning"]
                )
                for wrong_hero in hero_list:
                    embed.add_field(
                        name="{} / {}".format(wrong_hero['name'], wrong_hero['name_ru']),
                        value="Введи: !talent {} #лвла".format(wrong_hero['name_ru']),
                        inline=False
                    )
                embed.set_footer(
                    text=f"Информация для {context.message.author}"
                )
            elif len(hero_list) == 0:
                embed = discord.Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )
        await context.send(embed=embed)

    @commands.command(name="pn")
    async def hots_notes(self, context):
        """
        Информация по патчноутам
        """
        patchlink = 'https://heroespatchnotes.com/patch/summary.html'
        await context.send(patchlink)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(hots(bot))
