import json
import requests

from utils.classes.Hero import Hero

heroes_ru_json_file = 'data/heroesdata_ru.json'

with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
    heroes_ru_list = json.load(heroes_ru_json)
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'

hero = Hero('Самуро')


for data in heroes_ru_list.values():
    hero = Hero(data)
    folder = 'img/portrait/'
    thumb_url = 'https://nexuscompendium.com/images/portrait/'
    hero_name = hero.en.lower().replace('.', '').replace("'", "").replace(' ', '-')
    url = thumb_url + hero_name + '.png'
    path = folder + hero_name + '.png'
    r = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    with open(path, 'wb') as file:
        file.write(r.content)

    print(r.status_code)
    print(r.headers['content-type'])
    print(r.encoding)
    print('----------')
