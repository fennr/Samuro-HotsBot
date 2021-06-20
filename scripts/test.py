import requests
import json
import urllib.request
import xml.etree.ElementTree as ET
from pyxdameraulevenshtein import damerau_levenshtein_distance, normalized_damerau_levenshtein_distance
from bs4 import BeautifulSoup

patch_summary = 'https://heroespatchnotes.com/feed/patch-summary.xml'
stlk_file = 'c:\\Users\\Viktor\\Documents\\GitHub\\discord-bot\\data\\stlk_builds.txt'
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
        if (hero['name_ru'] == hero_name) or (hero['name'] == hero_name):
            return hero
    return None


def last_patch_notes():
    heroes_list = create_ru_list_heroes(stlk_file)
    print(heroes_list)
    response = requests.get(patch_summary)
    tree = ET.fromstring(response.text)
    # print(tree)
    for child in tree.find('{http://www.w3.org/2005/Atom}entry'):
        if child.tag == '{http://www.w3.org/2005/Atom}title':
            title = child.text
            print(title)
        if child.tag == '{http://www.w3.org/2005/Atom}content':
            # print(child.text)
            soup = BeautifulSoup(child.text, 'html.parser')
            for link in soup.findAll('a'):
                hero_url = link.get('href')
                hero = find_hero(link.text)
                if hero is not None:
                    print('Герой: {} \nПоследние изменения: {}'.format(hero['name_ru'], hero_url))


def find_hero2(hero_name):
    hero_name = hero_name.capitalize()
    good_distance = 3
    with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
        heroes_ru_list = json.load(heroes_ru_json)
    print(heroes_ru_list)
    for i in range(1, good_distance):
        for hero, data in heroes_ru_list.items():
            if (damerau_levenshtein_distance(hero_name, data['name_en'].capitalize()) < i) or \
                    (damerau_levenshtein_distance(hero_name, data['name_ru'].capitalize()) < i):
                #print('{} -> {}   | Погрешность: {} симв.'.format(hero_name, data['name_ru'], i))
                return data
            for nick in data['nick']:
                if damerau_levenshtein_distance(hero_name, nick.capitalize()) < i+1:
                    #print('{} -> {} -> {}  | Погрешность: {} симв.'.format(hero_name, nick, data['name_ru'], i+1))
                    return data
    return None


if __name__ == '__main__':
    #hero = find_hero2('Самуро')
    #print(hero)
    response = requests.get('https://heroespatchnotes.com/patch/summary.html')
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.ol.li.a)

