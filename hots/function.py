import json
import re
import os, sys, yaml
from discord import Embed, File
from hots.Hero import Hero
from helpers import sql, Error
from discord.ext import commands

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

heroes_ru_json_file = 'data/heroesdata_ru.json'


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + 1)  # transposition

    return int(d[lenstr1 - 1, lenstr2 - 1])


def read_hero_from_message(args, author=None, command='hero'):
    hero = None
    if len(args) == 0:
        raise commands.BadArgument('Не введен героя')
    else:
        hero_name = ' '.join(map(str, args))  # для имен из нескольких слов
        hero_list = find_heroes(hero_name)
        if len(hero_list) == 1:
            embed = None
            hero = hero_list[0]
        elif len(hero_list) > 1:
            embed = find_more_heroes(hero_list, author, command=command)
        else:
            embed = hero_not_found()
    return hero, embed


def args_not_found(command, lvl=''):
    embed = Embed(
        title="Ошибка! Введите все аргументы",
        color=config["error"]
    )
    embed.add_field(
        name="Пример:",
        value=f"_{config['bot_prefix']}{command} Самуро {lvl}_",
        inline=False
    )
    embed.set_footer(
        text=f"#help для просмотра справки по командам"  # context.message.author если использовать без slash
    )
    return embed


def hero_not_found():
    error = "Ошибка! Герой не найден"
    raise commands.CommandInvokeError(error)


def find_more_heroes(hero_list, author, command='hero', lvl=''):
    embed = Embed(
        title="Возможно вы имели в виду:",
        color=config["warning"]
    )
    for wrong_hero in hero_list:
        embed.add_field(
            name="{} / {}".format(wrong_hero.en, wrong_hero.ru),
            value=f"Введи: {config['bot_prefix']}{command} {wrong_hero.ru} {lvl}",
            inline=False
        )
    embed.set_footer(
        text=f"Информация для: {author}"
    )
    return embed


def open_hero(hero_name):
    with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
        heroes_ru_list = json.load(heroes_ru_json)
    for hero, data in heroes_ru_list.items():
        if hero_name == data['name_en'] or hero_name == data['name_ru'] or hero_name == hero:
            return data
    return None


def add_thumbnail(hero: Hero, embed):
    ext = '.png'
    thumb_url = 'https://nexuscompendium.com/images/portrait/'
    hero_name = hero.en.lower().replace('.', '').replace("'", "").replace(' ', '-')
    url = thumb_url + hero_name + ext
    '''
    folder = 'img/portrait/'
    path = folder + hero_name + ext
    filename = hero_name + ext
    file = File(path, filename=filename)
    #url = 'attachment://' + filename
    #print(url)
    '''
    embed.set_thumbnail(
        url=url
    )
    return embed


def find_heroes(hero_name, allowed_error=5):
    hero_name = hero_name.capitalize()
    hero_list = []
    with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
        heroes_ru_list = json.load(heroes_ru_json)
    # print(heroes_ru_list)
    for i in range(1, allowed_error):
        if (len(hero_name) < 3) and i > 1:  # исключить поиск коротких слов
            break
        if len(hero_list) == 0:
            for data in heroes_ru_list.values():
                hero = Hero(data)
                if (damerau_levenshtein_distance(hero_name, hero.en.capitalize()) < i) or \
                        (damerau_levenshtein_distance(hero_name, hero.ru.capitalize()) < i) or \
                        (damerau_levenshtein_distance(hero_name, hero.id.capitalize()) < i):
                    #print('{} -> {}   | Погрешность: {} симв.'.format(hero_name, data['name_ru'], i - 1))
                    if hero not in hero_list:
                        hero_list.append(hero)
                if (allowed_error - i) > 1:  # чтобы по прозвищам поиск был более строгий
                    for nick in hero.nick:
                        if damerau_levenshtein_distance(hero_name, nick.capitalize()) < i and hero not in hero_list:
                            print('{} -> {} -> {} | Погрешность: {} симв.'.format(hero_name, nick, hero.ru,
                                                                                  i - 1))
                            if hero not in hero_list:
                                hero_list.append(hero)
                                break
    return hero_list


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
        clean_r = re.compile('~~.{3,5}~~')
        left, dig, right = raw_text.split('~~', maxsplit=2)
        dig = float(dig) * 100
        clean_text = re.sub(clean_r, '(+{}% за лвл)'.format(dig), raw_text)
        return clean_text
    else:
        return raw_text