import json
import os
import sys

import yaml
from discord import Embed

from hots.function import cleanhtml
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

with open(heroes_json_file) as heroes_json:
    heroes_data = json.load(heroes_json)
with open(gamestrings_json_file, encoding='utf-8') as ru_json:
    ru_data = json.load(ru_json)


def read_talent_lvl(input):
    hero_name = ''
    for word in input:  # для героев из нескольких слов
        if not word.isdigit():
            hero_name += word + ' '
        else:
            hero_name = hero_name[:-1]
            lvl = word
            break
    return hero_name, lvl


def wrong_talent_lvl(author):
    embed = Embed(
        title="Ошибка! Выберете правильный уровень таланта",
        color=config["error"]
    )
    embed.set_footer(
        text=f"Информация для: {author}"  # context.message.author если использовать без slash
    )
    return embed


def talents(hero: Hero, lvl, author):
    lvl = str(lvl)
    full_hero = heroes_data[hero.id]
    level = 'level' + lvl
    talents_data = full_hero['talents'][level]
    embed = Embed(
        title="{} / {} : Таланты на {} уровне".format(hero.en, hero.ru, lvl),
        color=config["success"]
    )
    for i in range(len(talents_data)):
        talent_nameID = talents_data[i]['nameId']
        talent_buttonID = talents_data[i]['buttonId']
        talent_hotkey = talents_data[i]['abilityType']
        full_talent_name_en = talent_nameID + '|' + \
                              talent_buttonID + '|' + talent_hotkey + '|False'
        talent_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
        talent_desc_ru = cleanhtml(ru_data['gamestrings']['abiltalent']['full'][full_talent_name_en])
        embed.add_field(
            name='{} ({})'.format(talent_name_ru, talent_hotkey),
            value="{}".format(talent_desc_ru),
            inline=False
        )
        embed.set_footer(
            text=f"Информация для: {author}"  # context.message.author если использовать без slash
            # text=f"Текущий патч: {config['patch']}"
        )
    return embed
