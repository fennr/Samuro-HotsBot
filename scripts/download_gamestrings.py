import json
import os
import sys

import requests
import yaml

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

file = 'data/gamestrings'
patch = config["patch"]


def download_gamestrings(filename, patch_number):
    short_pn = patch_number[-5:]
    print(short_pn)
    gs_url = 'https://raw.githubusercontent.com/HeroesToolChest/heroes-data/master/heroesdata/' \
             + patch_number + '/gamestrings/gamestrings_' + short_pn + '_ruru.json'
    print(gs_url)
    response = requests.get(gs_url)
    filename = filename + short_pn + '.json'
    with open(filename, 'w', encoding='utf-8') as gamestrings_json:
        json.dump(response.json(), gamestrings_json, ensure_ascii=False, indent=4)


def test():
    print(config["patch"])


if __name__ == '__main__':
    download_gamestrings(file, patch)
    # test()
