import os
import re
from discord import Embed
from utils.classes.Hero import Hero
from utils.library import files
from utils.scripts import ytparser
from utils import exceptions
from utils.classes import Const

config = files.get_yaml("config.yaml")

jsons = Const.jsons


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
    raise exceptions.HeroNotFoundError


def find_more_heroes(hero_list, author, command='hero', lvl=''):
    if len(hero_list) > 0:
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
    else:
        raise exceptions.HeroNotFoundError
    return embed


def open_hero(hero_name):
    for hero, data in jsons.heroes_ru.items():
        if hero_name == data['name_en'] or hero_name == data['name_ru'] or hero_name == hero:
            return data
    return None


def find_heroes(hero_name, allowed_error=5):
    hero_name = hero_name.capitalize()
    hero_list = []
    for i in range(1, allowed_error):
        if (len(hero_name) < 3) and i > 1:  # исключить поиск коротких слов
            break
        if len(hero_list) == 0:
            for data in jsons.heroes_ru.values():
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
                            #print('{} -> {} -> {} | Погрешность: {} симв.'.format(hero_name, nick, hero.ru, i - 1))
                            if hero not in hero_list:
                                hero_list.append(hero)
                                break
    return hero_list


def get_hero(hero_name):
    heroes_list = find_heroes(hero_name)
    if len(heroes_list) == 1:
        return heroes_list[0]
    else:
        return heroes_list


def get_master_opinion(ctx, hero_name, embed=None):
    url = 'https://www.youtube.com/watch?v='
    if isinstance(hero_name, Hero):
        hero = hero_name
    else:
        hero = get_hero(hero_name)
    if isinstance(hero, list):
        embed = find_more_heroes(hero, ctx.message.author, command='pancho')
        return embed
    if isinstance(hero, Hero):
        videos = jsons.pancho.get(hero.id)
        if videos is not None:
            if len(videos) > 0:
                video = videos[0]
                if embed is not None:
                    text = ''
                    for video in videos:
                        text += f"[{video['date'][:10]}]({url}{video['url']})\n"
                    embed.add_field(
                        name="Мнение мастера",
                        value=text
                    )
                    return embed
                else:
                    return f"{url}{video['url']}"
        else:
            if embed is not None:
                return embed
            else:
                return "Для данного героя еще не было мнений мастера"


def add_master_opinion(hero_name, url):
    channel_name = "PanchoProduction"
    videos = ytparser.get_last_videos(os.environ.get('YT_API'), channel_name)
    yt, id = url.split('?v=', maxsplit=2)
    video = videos.get(id)
    if video is not None:
        hero = get_hero(hero_name)
        master_opinion_json = 'data/pancho.json'
        with open(master_opinion_json, encoding='utf-8') as File:
            master_json = jsons.load(File)
        item = master_json.get(hero.id)
        vid = dict(date=video['date'], title=video['title'], url=video['url'])
        if item is None:
            first_element = []
            first_element.append(vid)
            master_json[hero.id] = first_element
        else:
            master_json[hero.id].insert(0, vid)
        with open(master_opinion_json, 'w', encoding='utf-8') as result_file:
            jsons.dump(master_json, result_file, ensure_ascii=False, indent=4)
        return 0
    else:
        return 1


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