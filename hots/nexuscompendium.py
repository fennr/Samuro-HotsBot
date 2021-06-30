import os
import sys
import yaml
import json
from discord import Embed
from hots.function import open_hero

import requests


if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


short_patch = config["patch"][-5:]


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
        color=config["success"]
    )
    hero_links = ''
    for hero in heroes:
        hero_name = open_hero(hero['Name'])
        hero_links = hero_links + '[' + hero_name['name_ru'] + '](' + hero['URL'] + '), '
    hero_links = hero_links[:-2]
    embed.add_field(
        name="Герои текущей ротации",
        value=f"{hero_links}"
    )
    embed.set_footer(
        #text=f"Информация для: {author}"  # context.message.author если использовать без slash
        text=f"Текущий патч: {config['patch']}"
    )

    return embed