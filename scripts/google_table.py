import gspread
import time
import json

from hots.Hero import Hero

json_config = 'data/hots-stkr-b57fd2ec7336.json'
json_data = 'data/stlk_builds.json'

#Генерация json с билдами
def create_stlk_json():
    try:
        gc = gspread.service_account(filename=json_config)
        sh = gc.open('hots_stlk')
        sh_prod = gc.open_by_key('1WGYC347SntBIpF7ZrFXoCAAt2BqbYgw9EIbCuff_p8M')
        worksheet = sh_prod.get_worksheet(0)
        list_of_heroes = worksheet.get_all_values()
        heroes_dict = {}
        head = list_of_heroes[0]
        for hero_raw in list_of_heroes[1:]:
            hero_dict = dict(Hero_name=hero_raw[0], build1=hero_raw[1], comment1=hero_raw[2],
                             build2=hero_raw[3], comment2=hero_raw[4], build3=hero_raw[5], comment3=hero_raw[6])
            hero = Hero(hero_dict['Hero_name'])
            heroes_dict[hero.id] = hero_dict
        with open(json_data, 'w', encoding='utf-8') as write_file:
            json.dump(heroes_dict, write_file, indent=4, ensure_ascii=False)
        print('Файл STLK json записан')
    except:
        print("Ошибка записи билдов сталка")

#Создание json
'''
list_of_heroes = worksheet.get_all_records()
hero_dict = {}
for hero_raw in list_of_heroes:
    hero = open_hero(hero_raw['Hero_name'])
    print(hero)
    hero_dict[hero['name_id']] = hero_raw

with open(json_data, 'w', encoding='utf-8') as write_file:
    json.dump(hero_dict, write_file, indent=4, ensure_ascii=False)
print('Файл записан')'''

#Перезапись имен героев
'''
row = 2
column = 1
for raw_hero in list_of_heroes[row:]:
    hero = find_heroes(raw_hero['Hero_name'])[0]
    print(hero)
    worksheet.update_cell(row, column, hero['name_ru'])
    row += 1
    time.sleep(1)'''


if __name__ == '__main__':
    create_stlk_json()