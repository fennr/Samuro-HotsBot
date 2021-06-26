import os
import sys
import yaml
import json
from discord import Embed
from hots.function import open_hero, find_heroes, cleanhtml, per_lvl


if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'

with open(heroes_json_file) as heroes_json:
    heroes_data = json.load(heroes_json)
with open(gamestrings_json_file, encoding='utf-8') as ru_json:
    ru_data = json.load(ru_json)


def talents(hero, lvl, author):
    lvl = str(lvl)
    hero_json_file = 'hero/' + hero['name_json']
    with open(hero_json_file) as hero_json:
        hero_data = json.load(hero_json)
    full_hero = heroes_data[hero_data['cHeroId']]
    level = 'level' + lvl
    talents = full_hero['talents'][level]
    embed = Embed(
        title="{} / {} : Таланты на {} уровне".format(hero['name_en'], hero['name_ru'], lvl),
        color=config["success"]
    )
    for i in range(len(talents)):
        talent_name = hero_data['talents'][lvl][i]['name']
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
            text=f"Информация для: {author}"  # context.message.author если использовать без slash
            # text=f"Текущий патч: {config['patch']}"
        )
    return embed