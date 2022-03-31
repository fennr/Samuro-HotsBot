import json
import requests
from utils.classes.Const import config

file_path = '../../data/'

def download_gamestrings(dir):
    gs_file = 'gamestrings'
    gs_url = 'https://raw.githubusercontent.com/HeroesToolChest/heroes-data/master/heroesdata/' \
             + config.patch + '/gamestrings/gamestrings_' + config.short_patch + '_ruru.json'
    print(gs_url)
    response_gs = requests.get(gs_url)
    game_strings_file = dir + gs_file + config.short_patch + '.json'
    with open(game_strings_file, 'w', encoding='utf-8') as gamestrings_json:
        json.dump(response_gs.json(), gamestrings_json, ensure_ascii=False, indent=4)
    print(game_strings_file, 'записан')

    hd_file = 'heroesdata'
    hd_url = 'https://raw.githubusercontent.com/HeroesToolChest/heroes-data/master/heroesdata/' \
             + config.patch + '/data/herodata_' + config.short_patch + '_localized.json'
    print(hd_url)
    response_hd = requests.get(hd_url)
    hero_data_file = dir + hd_file + config.short_patch + '.json'
    with open(hero_data_file, 'w', encoding='utf-8') as herodata_json:
        json.dump(response_hd.json(), herodata_json, ensure_ascii=False, indent=4)
    print(hero_data_file, 'записан')


def test():
    print(config["patch"])


if __name__ == '__main__':
    download_gamestrings(file_path)
    # test()
