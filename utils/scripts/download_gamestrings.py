import json
import requests
from utils.library import files

config = files.get_yaml()

file_path = '../../data/'
patch = config["patch"]


def download_gamestrings(dir, patch_number):
    short_pn = patch_number[-5:]
    print(short_pn)
    gs_file = 'gamestrings'
    gs_url = 'https://raw.githubusercontent.com/HeroesToolChest/heroes-data/master/heroesdata/' \
             + patch_number + '/gamestrings/gamestrings_' + short_pn + '_ruru.json'
    print(gs_url)
    response_gs = requests.get(gs_url)
    game_strings_file = dir + gs_file + short_pn + '.json'
    with open(game_strings_file, 'w', encoding='utf-8') as gamestrings_json:
        json.dump(response_gs.json(), gamestrings_json, ensure_ascii=False, indent=4)
    print(game_strings_file, 'записан')

    hd_file = 'heroesdata'
    hd_url = 'https://raw.githubusercontent.com/HeroesToolChest/heroes-data/master/heroesdata/' \
             + patch_number + '/data/herodata_' + short_pn + '_localized.json'
    print(hd_url)
    response_hd = requests.get(hd_url)
    hero_data_file = dir + hd_file + short_pn + '.json'
    with open(hero_data_file, 'w', encoding='utf-8') as herodata_json:
        json.dump(response_hd.json(), herodata_json, ensure_ascii=False, indent=4)
    print(hero_data_file, 'записан')


def test():
    print(config["patch"])


if __name__ == '__main__':
    download_gamestrings(file_path, patch)
    # test()
