import os
import yaml
import json


def get_yaml(file: str = "config.yaml", path=""):
    if os.path.isfile(f"{path}{file}"):
        with open(f"{path}{file}") as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    elif os.path.isfile(f"../../{path}{file}"):
        with open(f"../../{path}{file}") as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        print(f"Файл {path}{file} не найден")


def get_json(file: str):
    if os.path.isfile(f"{file}"):
        with open(f"{file}", encoding="utf-8") as file:
            return json.load(file)
    elif os.path.isfile(f"../../{file}"):
        with open(f"../../{file}", encoding="utf-8") as file:
            return json.load(file)
    else:
        print(f"Файл {file} не найден")


def add_footer(embed):
    embed.set_footer(
        text=f"!help для просмотра справки по командам"
        # context.message.author если использовать без slash
    )
    return embed
