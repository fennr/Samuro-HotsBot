import os
import sys
import yaml
import requests
from discord import Embed
from hots.function import open_hero
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'


def last_pn(hero, author):
    patch_summary = 'https://heroespatchnotes.com/feed/patch-summary.xml'

    patchlink = 'https://heroespatchnotes.com/patch/summary.html'

    response = requests.get(patch_summary)
    tree = ET.fromstring(response.text)

    embed = Embed(
        title="{} / {} : Последний патч".format(hero['name_en'], hero['name_ru']),
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
                hero = open_hero(link.text)
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
        text=f"Информация для: {author}"
    )
    return embed