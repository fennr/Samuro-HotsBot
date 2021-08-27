import os
import sys
import xml.etree.ElementTree as ET

import requests
import yaml
from bs4 import BeautifulSoup
from discord import Embed

from hots.Hero import Hero

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata' + short_patch + '.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'


def get_last_update(url, embed=None):
    try:
        if embed is None:
            embed = Embed(
                title="Последние изменения героя",
                color=config["info"]
            )
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
        response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
        soup = BeautifulSoup(response.text, 'html.parser')
        patch = soup.findAll("div", {"class": "panel panel-primary"})
        name: str = "Последнее изменение героя"
        value = patch[0].h3  # берем только первый патч
        value_links = value.findAll('a', class_='pull-right')
        value_link = value_links[0].get('href')
        embed.add_field(
            name=name,
            value=f"[{value.text}]({value_link})",
            inline=False
        )
    except:
        pass
    return embed


def last_pn(hero=None, author=''):
    patch_summary = 'https://heroespatchnotes.com/feed/patch-summary.xml'

    patchlink = 'https://heroespatchnotes.com/patch/summary.html'

    response = requests.get(patch_summary)
    tree = ET.fromstring(response.text)
    if hero is not None:
        embed = Embed(
            title="{} / {} : Последний патч".format(hero['name_en'], hero['name_ru']),
            color=config["info"]
        )
    else:
        embed = Embed(
            title="Патчноут",
            color=config["info"]
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
            date, patch_number = title.split(' ', maxsplit=1)
        if child.tag == '{http://www.w3.org/2005/Atom}content':
            # print(child.text)
            soup = BeautifulSoup(child.text, 'html.parser')
            herolinks = ''
            for link in soup.findAll('a'):
                hero_url = link.get('href')
                hero = Hero(link.text)
                if hero is not None:
                    # herolinks = herolinks + '[' + hero['name_ru'] + '](' + hero_url + '), '
                    herolinks += hero.ru + ', '
                    # print('Герой: {} \nПоследние изменения: {}'.format(hero['name_ru'], hero_url))
            herolinks = herolinks[:-2]
            embed.add_field(
                name=f"Последние измененные герои ({date})",
                value=f"{herolinks}",
                inline=False
            )
    embed.set_footer(
        text=f"Информация для: {author}"
    )
    return embed
