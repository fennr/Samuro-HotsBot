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

def skill(hero, author):
    # сюда добавить проверки ввода аргументов, чтобы автоматом выводить нужный тип
    embed = skills(hero, 'basic', author)
    return embed

def skills(hero, ability_type, author):
    hero_json_file = 'hero/' + hero['name_json']
    with open(hero_json_file) as hero_json:
        hero_data = json.load(hero_json)
    full_hero = heroes_data[hero_data['cHeroId']]
    ability = full_hero['abilities'][ability_type]
    if ability_type == 'basic':
        type_text = 'Базовые'
    elif ability_type == 'heroic':
        type_text = 'Героические'
    else:
        type_text = 'Особые'
    embed = Embed(
        title="{} / {} : {} способности".format(hero['name_en'], hero['name_ru'], type_text),
        color=config["success"]
    )
    for i in range(len(ability)):  # считываем все абилки
        # считываем файл с переводом
        ability_name = hero_data['abilities'][hero_data['hyperlinkId']][i]['name']
        ability_nameID = ability[i]['nameId']
        ability_buttonID = ability[i]['buttonId']
        ability_hotkey = ability[i]['abilityType']
        try:
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
                name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                value="{}: _{}_\n{}".format(cooldown_title, cooldown_time, ability_desc_ru),
                inline=False
            )
        except:
            print(ability[i])
            embed.add_field(
                name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                value="{}".format(ability_desc_ru),
                inline=False
            )
    embed.set_footer(
        text=f"Информация для: {author}"  # context.message.author если использовать без slash
        # text=f"Текущий патч: {config['patch']}"
    )
    return embed

