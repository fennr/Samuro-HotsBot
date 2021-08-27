import os
import sys

import requests
import yaml
from discord import Embed
from hots.Hero import Hero
from hots.Hero import Hero

from hots.Hero import Hero
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]


def ranked():
    url = 'https://nexuscompendium.com/api/currently/ranked'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    data = response.json()
    start_date = data['Ranked']['StartDate']
    end_date = data['Ranked']['EndDate']
    name = data['Ranked']['Name'].replace('Season', 'сезон')
    embed = Embed(
        title='{} '.format(name),
        color=config["info"]
    )
    embed.add_field(
        name="Начало сезона",
        value=f"{start_date}",
        inline=True
    )
    embed.add_field(
        name="Конец сезона",
        value=f"{end_date}",
        inline=True
    )
    embed.set_footer(
        text=f"Текущий патч: {config['patch']}"
    )
    return embed


def sales():
    url = 'https://nexuscompendium.com/api/currently/sales'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    data = response.json()
    start_date = data['Sale']['StartDate']
    end_date = data['Sale']['EndDate']
    heroes = data['Sale']['Heroes']
    text = ''
    embed = Embed(
        title='{} : {} - {}'.format('Скидки на героев', start_date, end_date),
        color=config["info"]
    )
    count = 1
    for hero in heroes:
        hero_name = Hero(hero['Name'])
        text += str(count) + '. ' + hero_name.ru + ' - ' + str(hero['GemPrice']) + ' gems\n'
        count += 1
    embed.add_field(
        name="Текущие скидки",
        value=f"{text}"
    )
    embed.set_footer(
        text=f"Текущий патч: {config['patch']}"
    )
    return embed


def weekly_rotation():
    url = 'https://nexuscompendium.com/api/currently/herorotation'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    data = response.json()
    start_date = data['RotationHero']['StartDate']
    end_date = data['RotationHero']['EndDate']
    heroes = data['RotationHero']['Heroes']
    embed = Embed(
        title='{} : {} - {}'.format('Ротация героев', start_date, end_date),
        color=config["info"]
    )
    hero_links = ''
    for hero_name in heroes:
        hero = Hero(hero_name['Name'])
        hero_links = hero_links + '[' + hero.ru + '](' + hero_name['URL'] + '), '
    hero_links = hero_links[:-2]
    embed.add_field(
        name="Герои текущей ротации",
        value=f"{hero_links}"
    )
    embed.set_footer(
        # text=f"Информация для: {author}"  # context.message.author если использовать без slash
        text=f"Текущий патч: {config['patch']}"
    )

    return embed


if __name__ == '__main__':
    heroes = sales()
