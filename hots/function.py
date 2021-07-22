import json
import re

from pyxdameraulevenshtein import damerau_levenshtein_distance

heroes_ru_json_file = 'data/heroesdata_ru.json'


def open_hero(hero_name):
    with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
        heroes_ru_list = json.load(heroes_ru_json)
    for hero, data in heroes_ru_list.items():
        if hero_name == data['name_en'] or hero_name == data['name_ru'] or hero_name == hero:
            return data


def add_thumbnail(hero, embed):
    thumb_url = 'https://nexuscompendium.com/images/portrait/'
    hero_name = hero['name_en'].lower().replace('.', '').replace("'", "").replace(' ', '-')
    url = thumb_url + hero_name + '.png'
    print(url)
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
            for hero, data in heroes_ru_list.items():
                if (damerau_levenshtein_distance(hero_name, data['name_en'].capitalize()) < i) or \
                        (damerau_levenshtein_distance(hero_name, data['name_ru'].capitalize()) < i) or \
                        (damerau_levenshtein_distance(hero_name, hero.capitalize()) < i):
                    print('{} -> {}   | Погрешность: {} симв.'.format(hero_name, data['name_ru'], i - 1))
                    if data not in hero_list:
                        hero_list.append(data)
                if (allowed_error - i) > 1:  # чтобы по прозвищам поиск был более строгий
                    for nick in data['nick']:
                        if damerau_levenshtein_distance(hero_name, nick.capitalize()) < i and data not in hero_list:
                            print('{} -> {} -> {} | Погрешность: {} симв.'.format(hero_name, nick, data['name_ru'],
                                                                                  i - 1))
                            if data not in hero_list:
                                hero_list.append(data)
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
