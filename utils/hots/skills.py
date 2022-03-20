import json
import os
import sys

import yaml
from discord import Embed

from utils.library.hots import cleanhtml
from utils.classes.Hero import Hero
from utils.classes import Const
from utils.classes.Const import config, data, jsons

def wrong_btn_key():
    embed = Embed(
        title="Ошибка выбора клавиши".format(),
        color=config.error
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
        title="{} / {} : Cпособности".format(hero.en, hero.ru),
        color=config.success
    )
    for elem in types:
        embed = skill(hero, author, elem, embed, btn_key)
    return embed


def skill(hero: Hero, author=None, ability_type='basic', embed=None, key=None):
    full_hero = data.heroes[hero.id]
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
            color=config.success
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
            ability_name_ru = data.heroes_ru['gamestrings']['abiltalent']['name'][full_talent_name_en]
        except:
            full_talent_name_en = ability_nameID + '|' + \
                                  ability_buttonID + '|' + ability_hotkey + '|True'
            ability_name_ru = data.heroes_ru['gamestrings']['abiltalent']['name'][full_talent_name_en]
        ability_desc_ru = cleanhtml(data.heroes_ru['gamestrings']['abiltalent']['full'][full_talent_name_en])
        try:  # может не быть кулдауна
            # ability_desc = hero_data['abilities'][hero_data['cHeroId']][i]['description']
            ability_cooldown = cleanhtml(data.heroes_ru['gamestrings']['abiltalent']['cooldown'][full_talent_name_en])
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
    )
    return embed
