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
heroes_json_file = 'data/heroesdata.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'

with open(heroes_json_file) as heroes_json:
    heroes_data = json.load(heroes_json)
with open(gamestrings_json_file, encoding='utf-8') as ru_json:
    ru_data = json.load(ru_json)


def wrong_btn_key():
    embed = Embed(
        title="Ошибка выбора клавиши".format(),
        color=config["error"]
    )
    embed.add_field(
        name='После имени введите клавиши нужных способности (можно на русском)',
        value="Например: #skill самуро qwe|йцу",
        inline=False
    )
    return embed


def read_skill_btn(input):
    if len(input) == 1:
        hero_name = input[0]
        btn = 'QWE'
    else:
        hero_name = ' '.join(map(str, input[:-1]))
        btn = input[-1]
    return hero_name, btn


def skills(hero: Hero, author, types=None, btn_key=None):
    if types is None:
        types = ['basic']
    embed = Embed(
        title="{} / {} : Cпособности".format(hero['name_en'], hero['name_ru']),
        color=config["success"]
    )
    for elem in types:
        embed = skill(hero, author, elem, embed, btn_key)
    return embed


def skill(hero: Hero, author=None, ability_type='basic', embed=None, key=None):
    full_hero = heroes_data[hero.id]
    ability = full_hero['abilities'][ability_type]
    if ability_type == 'basic':
        type_text = 'Базовые'
    elif ability_type == 'heroic':
        type_text = 'Героические'
    else:
        type_text = 'Особые'
    if embed is None:
        embed = Embed(
            title="{} / {} : {} cпособности".format(hero.en, hero.ru, type_text),
            color=config["success"]
        )
    for i in range(len(ability)):  # считываем все абилки
        # считываем файл с переводом
        ability_nameID = ability[i]['nameId']
        ability_buttonID = ability[i]['buttonId']
        ability_hotkey = ability[i]['abilityType']
        if key is not None:  # если есть аргумент с кнопками
            abil_keys = key.upper()
            good_key = {'Й': 'Q', 'Ц': 'W', 'У': 'E', 'В': 'D', 'К': 'R'}
            keys = []
            for abil_key in abil_keys:
                if abil_key in good_key.keys():
                    abil_key = good_key.get(abil_key)
                if abil_key not in good_key.values():
                    embed = wrong_btn_key()
                abil_key = 'Trait' if abil_key == 'D' else abil_key
                abil_key = 'Heroic' if abil_key == 'R' else abil_key
                keys.append(abil_key)
            if ability_hotkey not in keys:
                continue
        try:  # может быть True и False
            full_talent_name_en = ability_nameID + '|' + \
                                  ability_buttonID + '|' + ability_hotkey + '|False'
            ability_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
        except:
            full_talent_name_en = ability_nameID + '|' + \
                                  ability_buttonID + '|' + ability_hotkey + '|True'
            ability_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
        ability_desc_ru = cleanhtml(ru_data['gamestrings']['abiltalent']['full'][full_talent_name_en])
        try:  # может не быть кулдауна
            # ability_desc = hero_data['abilities'][hero_data['cHeroId']][i]['description']
            ability_cooldown = cleanhtml(ru_data['gamestrings']['abiltalent']['cooldown'][full_talent_name_en])
            cooldown_title, cooldown_time = ability_cooldown.split(':', 1)
            embed.add_field(
                name='{} ({})'.format(ability_name_ru, ability_hotkey),
                value="{}: _{}_\n{}".format(cooldown_title, cooldown_time, ability_desc_ru),
                inline=False
            )
        except:
            print(ability[i])
            embed.add_field(
                name='{} ({})'.format(ability_name_ru, ability_hotkey),
                value="{}".format(ability_desc_ru),
                inline=False
            )
    embed.set_footer(
        text=f"Информация для: {author}"  # context.message.author если использовать без slash
        # text=f"Текущий патч: {config['patch']}"
    )
    return embed
