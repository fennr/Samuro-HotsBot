import json
from discord import Embed
from utils.library.hots import cleanhtml
from utils.classes.Hero import Hero
from utils.library import files
from utils import exceptions
from utils.classes.Const import config, data, jsons


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
        color=config.error
    )
    embed.set_footer(
        text=f"Информация для: {author}"  # context.message.author если использовать без slash
    )
    return embed


def talents(hero: Hero, lvl, author):
    lvl = str(lvl)
    full_hero = jsons.heroes[hero.id]
    level = 'level' + lvl
    try:
        talents_data = full_hero['talents'][level]
    except KeyError:
        raise exceptions.WrongTalentLvl
    embed = Embed(
        title="{} / {} : Таланты на {} уровне".format(hero.en, hero.ru, lvl),
        color=config.success
    )
    for i in range(len(talents_data)):
        talent_nameID = talents_data[i]['nameId']
        talent_buttonID = talents_data[i]['buttonId']
        talent_hotkey = talents_data[i]['abilityType']
        full_talent_name_en = talent_nameID + '|' + \
                              talent_buttonID + '|' + talent_hotkey + '|False'
        talent_name_ru = jsons.gamestrings['gamestrings']['abiltalent']['name'][full_talent_name_en]
        talent_desc_ru = cleanhtml(jsons.gamestrings['gamestrings']['abiltalent']['full'][full_talent_name_en])
        embed.add_field(
            name='{} ({})'.format(talent_name_ru, talent_hotkey),
            value="{}".format(talent_desc_ru),
            inline=False
        )
        embed.set_footer(
            text=f"Информация для: {author}"  # context.message.author если использовать без slash
        )
    return embed
