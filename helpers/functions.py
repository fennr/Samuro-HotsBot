import os
import yaml

def get_config():
    if not os.path.isfile("config.yaml"):
        # sys.exit("'config.yaml' not found! Please add it and try again.")
        with open("../config.yaml") as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        with open("config.yaml") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

def get_heroesdata_ru():
    if not os.path.isfile("data/heroesdata_ru.json"):
        # sys.exit("'config.yaml' not found! Please add it and try again.")
        with open("../data/heroesdata_ru.json") as file:
            return "../data/heroesdata_ru.json"
    else:
        with open("data/heroesdata_ru.json") as file:
            return "data/heroesdata_ru.json"

def get_pancho():
    if not os.path.isfile("data/pancho.json"):
        # sys.exit("'config.yaml' not found! Please add it and try again.")
        with open("../data/pancho.json") as file:
            return "../data/pancho.json"
    else:
        with open("data/pancho.json") as file:
            return "data/pancho.json"

def add_footer(embed):
    embed.set_footer(
        text=f"!help для просмотра справки по командам"
        # context.message.author если использовать без slash
    )
    return embed