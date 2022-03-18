import json
import csv
from utils.library import hots, base
from utils.classes.Hero import Hero

config = base.get_config()

if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v='
    master_opinion_json = '../data/pancho.json'
    with open('../../data/masters_opinion.csv', newline='', encoding='utf-8') as File:
        reader = csv.DictReader(File, fieldnames=['Hero', 'title', 'url', 'Date'], dialect='excel', delimiter=';')
        heroes = {}
        for row in reader:
            hero = hots.get_hero(row['Hero'])
            if isinstance(hero, Hero):
                item = heroes.get(hero.id)
                video = dict(date=row['Date'], title=row['title'], url=row['url'])
                if item is None:
                    first_element = []
                    first_element.append(video)
                    heroes[hero.id] = first_element
                else:
                    heroes[hero.id].append(video)

        #pprint(heroes)
        with open(master_opinion_json, 'w', encoding='utf-8') as result_file:
            json.dump(heroes, result_file, ensure_ascii=False, indent=4)
        print('Файл мнений мастера был записан')
            #print(f"{row['Hero']}: {url}{row['URL']}")



