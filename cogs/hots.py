import json
import os
import re
import sys
import yaml
import requests

import discord
from discord.ext import commands

from pyxdameraulevenshtein import damerau_levenshtein_distance

import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata.json'
stlk_file = 'data/stlk_builds.txt'
heroes_ru_json_file = 'data/heroesdata_ru.json'

def create_ru_list_heroes(filename):
    """
    Генерирует список героев на русском

    :param filename: Путь до файла
    :return: Список геров (list)
    """
    ru_heroes_list = []
    # heroes_txt = urlopen(filename.download_url).read()
    # heroes_txt = heroes_txt.decode('cp1251').splitlines()
    with open(filename, 'r', encoding='cp1251') as heroes_txt:
        for line in heroes_txt:
            if len(line) > 0:
                hero_ru, tail = line.split(sep='/', maxsplit=1)
                hero_en, tail = tail.split(sep=' — ', maxsplit=1)
                stlk_url, tail = tail.split(sep=' ', maxsplit=1)
                tail = tail[1:-2]
                shortbuild, hero_name = tail.split(sep=',')
                heroes = dict(name_ru=hero_ru, name_en=hero_en, name=hero_name, build=shortbuild, url=stlk_url)
                ru_heroes_list.append(heroes)

    return ru_heroes_list


def find_hero(hero_name):
    """
    Поиск героя по имени на русском или английском

    :param hero_name:Имя героя (string)
    :return: Имя героя (string)
    """
    hero_name = hero_name.capitalize()
    stlk_file = 'data/stlk_builds.txt'
    heroes_list = create_ru_list_heroes(stlk_file)
    for hero in heroes_list:
        if (hero['name_ru'] == hero_name) or (hero['name'] == hero_name) or (hero['name_en'] == hero_name):
            return hero
    return None


def find_hero2(hero_name, allowed_error=5):
    hero_name = hero_name.capitalize()
    hero_list = []
    with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
        heroes_ru_list = json.load(heroes_ru_json)
    #print(heroes_ru_list)
    for i in range(1, allowed_error):
        if (len(hero_name) < 3) and i > 1: #исключить поиск коротких слов
            break
        if len(hero_list) == 0:
            for hero, data in heroes_ru_list.items():
                if (damerau_levenshtein_distance(hero_name, data['name_en'].capitalize()) < i) or \
                        (damerau_levenshtein_distance(hero_name, data['name_ru'].capitalize()) < i) or \
                        (damerau_levenshtein_distance(hero_name, hero.capitalize()) < i):
                    print('{} -> {}   | Погрешность: {} симв.'.format(hero_name, data['name_ru'], i-1))
                    if data not in hero_list:
                        hero_list.append(data)
                if (allowed_error - i) > 1: #чтобы по прозвищам поиск был более строгий
                    for nick in data['nick']:
                        if damerau_levenshtein_distance(hero_name, nick.capitalize()) < i and data not in hero_list:
                            print('{} -> {} -> {} | Погрешность: {} симв.'.format(hero_name, nick, data['name_ru'], i-1))
                            if data not in hero_list:
                                hero_list.append(data)
                                break
    return hero_list


def find_wrong_hero(hero_name):
    """
    Поиск героя на русском или английском, с возможностью ошибки

    :param hero_name: Имя героя (string)
    :return: Список героев (list)
    """
    hero_name = hero_name.capitalize()
    stlk_file = 'data/stlk_builds.txt'
    heroes_list = create_ru_list_heroes(stlk_file)
    wrong_list = []
    for hero in heroes_list:
        if (hero['name_ru'][:3] == hero_name[:3]) or (hero['name'][:3] == hero_name[:3]) or \
                (hero['name_ru'][-3:] == hero_name[-3:]) or (hero['name'][:3] == hero_name[:3]) or \
                (hero['name_en'][-3:] == hero_name[-3:]) or (hero['name_en'][:3] == hero_name[:3]):
            wrong_list.append(hero)
    return wrong_list


def cleanhtml(raw_html):
    """
    Удаляет html теги из текста

    :param raw_html: Строка
    :return: Строка без </.*?>
    """
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return per_lvl(cleantext)


def per_lvl(raw_text):
    """
    Заменяет ~~ на проценты в тексте

    :param raw_text: Строка с ~~*~~
    :return: Строка с % за уровень
    """
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

    guild_ids = [845658540341592096]  # Put your server ID in this array.

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.command(name="patchnotes")
    async def hots_notes(self, context):
        """
        Информация по патчноутам
        Список измененных в последнем патче героев (кликабельно)
        -----
        """
        patch_summary = 'https://heroespatchnotes.com/feed/patch-summary.xml'

        patchlink = 'https://heroespatchnotes.com/patch/summary.html'
        heroes_list = create_ru_list_heroes(stlk_file)
        print(heroes_list)
        response = requests.get(patch_summary)
        tree = ET.fromstring(response.text)

        embed = discord.Embed(
            title="Патчноут",
            color=config["info"]
        )
        embed.add_field(
            name="Список всех патчей",
            value=f"{patchlink}",
            inline=False
        )
        response = requests.get('https://heroespatchnotes.com/patch/summary.html')
        soup = BeautifulSoup(response.text, 'html.parser')
        embed.add_field(
            name="Последний патч",
            value=f"[{soup.ol.li.a.text}]({soup.ol.li.a['href']})",
            inline=False
        )
        print(soup.ol.li.a)
        for child in tree.find('{http://www.w3.org/2005/Atom}entry'):
            if child.tag == '{http://www.w3.org/2005/Atom}title':
                title = child.text
            if child.tag == '{http://www.w3.org/2005/Atom}content':
                # print(child.text)
                soup = BeautifulSoup(child.text, 'html.parser')
                herolinks = ''
                for link in soup.findAll('a'):
                    hero_url = link.get('href')
                    hero = find_hero(link.text)
                    if hero is not None:
                        herolinks = herolinks + '[' + hero['name_ru'] + '](' + hero_url + '), '
                        # print('Герой: {} \nПоследние изменения: {}'.format(hero['name_ru'], hero_url))
                herolinks = herolinks[:-2]
                embed.add_field(
                    name=f"Последние измененные герои ({title})",
                    value=f"{herolinks}",
                    inline=False
                )
        embed.set_footer(
            # text=f"Информация для {context.author}"
            text=f"Текущий патч: {config['patch']}"
        )
        await context.send(embed=embed)


    @commands.command(name="hero")
    async def hots_hero(self, context, *args):
        """
        Описание героя и ссылки на билды и разборы
        :param args: Имя героя
        -----
        """

        global hero_energytype
        heroespn_url = 'https://heroespatchnotes.com/hero/'  # + '.html'
        heroeshearth_top_url = 'https://heroeshearth.com/hero/'
        heroeshearth_all_url = 'https://heroeshearth.com/builds/hero/'
        icy_veins_url = 'https://www.icy-veins.com/heroes/'  # + '-build-guide'
        heroesfire_url = 'https://www.heroesfire.com/hots/wiki/heroes/'
        blizzhero_url = 'https://blizzardheroes.ru/guides/'

        if len(args) == 0:
            embed = discord.Embed(
                title="После команды введите имя героя на русском или английском",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config['bot_prefix']}hero Самуро_",
                inline=False
            )
        else:
            hero = None
            hero_list = find_hero2(args[0])
            if len(hero_list) == 1:
                hero = hero_list[0]
            elif len(hero_list) == 0:
                embed = discord.Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )
            elif len(hero_list) > 1:
                hero = None
                embed = discord.Embed(
                    title="Возможно вы имели в виду:",
                    color=config["warning"]
                )
                for wrong_hero in hero_list:
                    embed.add_field(
                        name="{} / {}".format(wrong_hero['name_en'], wrong_hero['name_ru']),
                        value=f"Введи: {config['bot_prefix']}hero {wrong_hero['name_ru']}",
                        inline=False
                    )
                embed.set_footer(
                    # text=f"Информация для {context.author}"
                    text=f"Текущий патч: {config['patch']}"
                )
            if hero is not None:
                with open(heroes_json_file) as heroes_json:
                    heroes_data = json.load(heroes_json)
                with open(gamestrings_json_file, encoding='utf-8') as ru_json:
                    ru_data = json.load(ru_json)
                hero_json_file = 'hero/' + hero['name_json']
                with open(hero_json_file) as hero_json:
                    hero_data = json.load(hero_json)
                hero_name = hero_data['cHeroId']
                hero_unit = ru_data['gamestrings']['unit']
                hero_description = hero_unit['description'][hero_name]
                hero_difficulty = hero_unit['difficulty'][hero_name]
                hero_expandedrole = hero_unit['expandedrole'][hero_name]

                full_hero = heroes_data[hero_data['cHeroId']]
                hero_life = full_hero['life']['amount']
                hero_energy = None
                try:
                    hero_energy = full_hero['energy']['amount']
                    hero_energytype = hero_unit['energytype'][hero_name]
                except:
                    pass

                embed = discord.Embed(
                    title='{} / {} ({})'.format(hero['name_en'], hero['name_ru'], hero_expandedrole), #title="Описание героя:",
                    color=config["success"]
                )
                '''embed.set_author(
                    name='{} / {}'.format(hero['name'], hero['name_ru'])
                )'''
                embed.add_field(
                    name="Описание",
                    value="{}".format(hero_description),
                    inline=False
                )
                embed.add_field(
                    name="Сложность",
                    value="{}".format(hero_difficulty),
                    inline=True
                )
                embed.add_field(
                    name="Здоровье",
                    value="{}".format(hero_life),
                    inline=True
                )
                if hero_energy is not None:
                    embed.add_field(
                        name="{}".format(hero_energytype),
                        value="{}".format(hero_energy),
                        inline=True
                    )
                default_hero_name = hero['name_en'].lower().replace('.', '').replace("'", "")
                heroespn_url_full = heroespn_url + default_hero_name.replace(' ', '') + '.html'
                embed.add_field(
                    name="Последние патчноуты героя:",
                    value="{}".format(heroespn_url_full),
                    inline=False
                )
                embed.add_field(
                    name="HeroesHearth / лучшая подборка билдов:",
                    value="{}{}".format(heroeshearth_top_url, default_hero_name.replace(' ', '-')),
                    inline=False
                )
                icy_veins_url_full = icy_veins_url + hero['name_en'].lower().replace(' ', '-').replace('.', '-').replace("'", "") + '-build-guide'
                icy_veins_url_full = icy_veins_url_full.replace('--', '-')
                embed.add_field(
                    name="Icy Veins / очень подробный разбор героя:",
                    value="{}".format(icy_veins_url_full),
                    inline=False
                )
                embed.add_field(
                    name="Heroesfire / Пользовательские билды",
                    value="{}{}".format(heroesfire_url, default_hero_name.replace(' ', '-')),
                    inline=False
                )
                embed.add_field(
                    name="Blizzhero / ру сайт",
                    value="{}{}".format(blizzhero_url, default_hero_name.replace(' ', '')),
                    inline=False
                )
                embed.set_footer(
                    #text=f"Информация для {context.author}"  # context.message.author если использовать без slash
                    text =f"Текущий патч: {config['patch']}"
                )

        await context.send(embed=embed)

    @commands.command(name="skill")
    async def hots_skill(self, context, *args):
        """
        Информация о скиллах героя
        :param args: Имя героя
        -----
        """
        # json с данными по всем героям
        with open(heroes_json_file) as heroes_json:
            heroes_data = json.load(heroes_json)

        # json с внутриигровыми строками перевода текста
        with open(gamestrings_json_file, encoding='utf-8') as ru_json:
            ru_data = json.load(ru_json)

        if len(args) == 0:
            embed = discord.Embed(
                title="После команды введите имя героя",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config['bot_prefix']}skill Самуро_",
                inline=False
            )
        else:
            hero = None
            hero_list = find_hero2(args[0])
            if len(hero_list) == 1:
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = discord.Embed(
                    title="Возможно вы имели в виду:",
                    color=config["warning"]
                )
                for wrong_hero in hero_list:
                    embed.add_field(
                        name="{} / {}".format(wrong_hero['name_en'], wrong_hero['name_ru']),
                        value=f"Введи: _{config['bot_prefix']}skill {wrong_hero['name_ru']}_",
                        inline=False
                    )
                embed.set_footer(
                    # text=f"Информация для {context.author}"
                    text=f"Текущий патч: {config['patch']}"
                )
            elif len(hero_list) == 0:
                embed = discord.Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )
            if hero is not None:
                # json по отдельному герою, содержит более детальную информацию
                hero_json_file = 'hero/' + hero['name_json']
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
                    ability_name = hero_data['abilities'][hero_data['hyperlinkId']][i]['name']
                    ability_nameID = ability[i]['nameId']
                    ability_buttonID = ability[i]['buttonId']
                    ability_hotkey = ability[i]['abilityType']
                    full_talent_name_en = ability_nameID + '|' + \
                                          ability_buttonID + '|' + ability_hotkey + '|False'
                    ability_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
                    try: # может не быть кулдауна
                        #ability_desc = hero_data['abilities'][hero_data['cHeroId']][i]['description']
                        ability_cooldown = cleanhtml(ru_data['gamestrings']['abiltalent']['cooldown'][full_talent_name_en])
                        cooldown_title, cooldown_time = ability_cooldown.split(':', 1)
                        ability_desc_ru = cleanhtml(ru_data['gamestrings']['abiltalent']['full'][full_talent_name_en])
                        embed.add_field(
                            name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                            value="{}: _{}_\n{}".format(cooldown_title, cooldown_time, ability_desc_ru),
                            inline=False
                        )
                    except:
                        print(ability[i])
                        embed.add_field(
                            name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                            value="{}".format(ability_desc_ru),
                            inline=False
                        )
                embed.set_footer(
                    text=f"Текущий патч: {config['patch']}"
                )
        await context.send(embed=embed)

    @commands.command(name="talent")
    async def hots_talent(self, context, *args):
        """
        Информация о талантах героя
        :param args: Имя героя и уровень талантов
        -----
        """
        # json с данными по всем героям
        with open(heroes_json_file) as heroes_json:
            heroes_data = json.load(heroes_json)

        # json с внутриигровыми строками перевода текста
        with open(gamestrings_json_file, encoding='utf-8') as ru_json:
            ru_data = json.load(ru_json)
        if len(args) < 2:
            embed = discord.Embed(
                title="После команды введите имя героя и уровень таланта",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config['bot_prefix']}talent Самуро 13_",
                inline=False
            )
        else:
            hero = None
            hero_list = find_hero2(args[0])
            if len(hero_list) == 1:
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = discord.Embed(
                    title="Возможно вы имели в виду:",
                    color=config["warning"]
                )
                for wrong_hero in hero_list:
                    embed.add_field(
                        name="{} / {}".format(wrong_hero['name_en'], wrong_hero['name_ru']),
                        value=f"_Введи: {config['bot_prefix']}talent {wrong_hero['name_ru']} лвл_",
                        inline=False
                    )
                embed.set_footer(
                    # text=f"Информация для {context.author}"
                    text=f"Текущий патч: {config['patch']}"
                )
            elif len(hero_list) == 0:
                embed = discord.Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )
            if hero is not None:
                # json по отдельному герою, содержит более детальную информацию
                hero_json_file = 'hero/' + hero['name_json']
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
                        embed.set_footer(
                            text=f"Текущий патч: {config['patch']}"
                        )
                else:
                    embed = discord.Embed(
                        title="Ошибка! Выберете правильный уровень таланта",
                        color=config["error"]
                    )
        await context.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(hots(bot))
