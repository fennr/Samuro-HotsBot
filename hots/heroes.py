import json
import os
import sys

import yaml
from discord import Embed

from hots.function import add_thumbnail, cleanhtml
from hots.patchnotes import get_last_update

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata' + short_patch + '.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'
stlk_json_file = 'data/stlk_builds.json'

with open(heroes_json_file) as heroes_json:
    heroes_data = json.load(heroes_json)
with open(gamestrings_json_file, encoding='utf-8') as ru_json:
    ru_data = json.load(ru_json)
with open(stlk_json_file, encoding='utf-8') as ru_json:
    stlk_data = json.load(ru_json)


def heroes_description_short(hero, author):
    hero_json_file = 'hero/' + hero['name_json']
    with open(hero_json_file) as hero_json:
        hero_data = json.load(hero_json)
    hero_name = hero_data['cHeroId']
    hero_unit = ru_data['gamestrings']['unit']
    hero_description = hero_unit['description'][hero_name]
    hero_expandedrole = hero_unit['expandedrole'][hero_name]

    full_hero = heroes_data[hero_data['cHeroId']]

    hero_complexity = int(full_hero['ratings']['complexity'])

    tier_desc = {
        'S': '(лучший выбор)',
        'A': '(сильный выбор)',
        'B': '(достойный выбор)',
        'C': '(ситуативный выбор)'
    }

    embed = Embed(
        title='{} / {} ({})'.format(hero['name_en'], hero['name_ru'], hero_expandedrole),
        # title="Описание героя:",
        color=config["success"]
    )
    embed.add_field(
        name="Описание",
        value="{}".format(cleanhtml(hero_description)),
        inline=False
    )
    embed.add_field(
        name="Сложность",
        value="{} / 10".format(hero_complexity),
        inline=True
    )
    embed.add_field(
        name="Позиция в мете",
        value="Тир {} {}".format(hero['tier'], tier_desc.setdefault(hero['tier'])),
        inline=True
    )
    return embed


def heroes_description(hero, author):
    hero_json_file = 'hero/' + hero['name_json']
    with open(hero_json_file) as hero_json:
        hero_data = json.load(hero_json)

    full_hero = heroes_data[hero_data['cHeroId']]
    hero_name = hero_data['cHeroId']
    hero_unit = ru_data['gamestrings']['unit']
    hero_description = hero_unit['description'][hero_name]
    hero_expandedrole = hero_unit['expandedrole'][hero_name]

    embed = Embed(
        title='{} / {} : Характеристики'.format(hero['name_en'], hero['name_ru']),
        # title="Описание героя:",
        color=config["success"]
    )
    embed.add_field(
        name="Описание",
        value="{}".format(cleanhtml(hero_description)),
        inline=False
    )
    embed.add_field(
        name="Роль",
        value="{}".format(hero_expandedrole),
        inline=True
    )
    hero_life = int(full_hero['life']['amount'])
    embed.add_field(
        name="Здоровье",
        value="{}".format(hero_life),
        inline=True
    )
    hero_ratings = full_hero['ratings']
    embed.add_field(
        name="Сложность",
        value="{} / 10".format(int(hero_ratings['complexity'])),
        inline=True
    )
    embed.add_field(
        name="Урон",
        value="{} / 10".format(int(hero_ratings['damage'])),
        inline=True
    )
    embed.add_field(
        name="Выживаемость",
        value="{} / 10".format(int(hero_ratings['survivability'])),
        inline=True
    )
    embed.add_field(
        name="Поддержка",
        value="{} / 10".format(int(hero_ratings['utility'])),
        inline=True

    )
    try:
        hero_damage = full_hero['weapons'][0]
        range_text = 'Ближний бой' if float(hero_damage['range']) <= 2.0 else str(hero_damage['range']) + ' м.'
        embed.add_field(
            name="Автоатаки",
            value="{} урона, каждые {} сек.".format(
                int(hero_damage["damage"]),
                hero_damage['period']),
            inline=True
        )
        embed.add_field(
            name="Дальность",
            value="{}".format(range_text),
            inline=True
        )
    except:
        print("Нет оружия")
    embed = add_thumbnail(hero, embed)
    embed.set_footer(
        text=f"Информация для: {author}"  # context.message.author если использовать без slash
        # text=f"Текущий патч: {config['patch']}"
    )
    return embed


def embed_stlk_builds(hero, author, embed=None, ad=False):
    name = 'Билды от Сталка'
    description = '**для вставки в чат игры**\n'
    if embed is None:
        name = 'для вставки в чат игры'
        description = ''
        embed = Embed(
            title=f"Билды от грандмастера STLK на героя {hero['name_ru']}",  # title="Описание героя:",
            color=config["success"]
        )
    stlk_builds = stlk_data[hero['name_id']]
    description += '💬 ' + stlk_builds['comment1'] + '\n```' + stlk_builds['build1'] + '```'
    if len(stlk_builds['build2']) > 0:
        description += '\n💬 ' + stlk_builds['comment2'].capitalize() + '\n```' + stlk_builds['build2'] + '```'
    if len(stlk_builds['build3']) > 0:
        description += '\n💬 ' + stlk_builds['comment2'].capitalize() + '\n```' + stlk_builds['build3'] + '```'
    embed.add_field(
        name=name,
        value=description,
        inline=False
    )
    if ad:
        embed.add_field(
            name="Задать вопросы по билдам можно на его стримах",
            value=f"[Перейти на твич @stlk](https://www.twitch.tv/stlk)",
            inline=False
        )
    return embed


def builds(hero, author, embed=None):
    heroespn_url = 'https://heroespatchnotes.com/hero/'  # + '.html'
    heroeshearth_top_url = 'https://heroeshearth.com/hero/'
    heroeshearth_all_url = 'https://heroeshearth.com/builds/hero/'
    icy_veins_url = 'https://www.icy-veins.com/heroes/'  # + '-build-guide'
    heroesfire_url = 'https://www.heroesfire.com/hots/wiki/heroes/'
    blizzhero_url = 'https://blizzardheroes.ru/guides/'
    nexuscompendium_url = 'https://nexuscompendium.com/heroes/'
    default_hero_name = hero['name_en'].lower().replace('.', '').replace("'", "")
    heroespn_url_full = heroespn_url + default_hero_name.replace(' ', '') + '.html'
    heroesprofile_url = 'https://www.heroesprofile.com/Global/Talents/?hero='
    hotslogs_url = 'https://www.hotslogs.com/Sitewide/TalentDetails?Hero='
    if embed is None:
        embed = Embed(
            title='{} / {} : Билды'.format(hero['name_en'], hero['name_ru'], ),  # title="Описание героя:",
            color=config["success"]
        )
    icy_veins_url_full = icy_veins_url + hero['name_en'].lower().replace(' ', '-').replace('.',
                                                                                           '-').replace("'",
                                                                                                        "") + '-build-guide'
    icy_veins_url_full = icy_veins_url_full.replace('--', '-')

    embed = get_last_update(heroespn_url_full, embed)
    embed.add_field(
        name="Ссылки",
        value="[Патчноуты героя]({})\n" \
              "[Подборка билдов от HeroesHearth]({})\n" \
              "[Разбор героя от IcyVeins]({})\n" \
              "[Описание героя Nexuscompendium]({})\n" \
              "[Пользовательские билды HeroesFire]({})\n" \
              "[Винрейт по талантам HeroesProfile]({})\n" \
              "[Винрейт по талантам HotsLogs]({})".format(
            heroespn_url_full,
            heroeshearth_top_url + default_hero_name.replace(' ', '-'),
            icy_veins_url_full,
            nexuscompendium_url + default_hero_name.replace(' ', '-'),
            heroesfire_url + default_hero_name.replace(' ', '-'),
            heroesprofile_url + hero['name_en'].replace(' ', '+') + '&league_tier=master,diamond',
            hotslogs_url + hero['name_en'].replace(' ', '%20')
        ),
        inline=False
    )
    embed = embed_stlk_builds(hero, author, embed)
    embed.set_footer(
        text=f"Информация для: {author}"  # context.message.author если использовать без slash
        # text=f"Текущий патч: {config['patch']}"
    )

    return embed
