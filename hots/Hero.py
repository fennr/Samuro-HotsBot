import json


class Hero:
    bug_names = {
        'Deckard Cain': 'Deckard',
        'Lúcio': 'Lucio'
    }

    def __init__(self, hero_name: str, bug_names=bug_names):
        heroes_ru_json_file = 'data/heroesdata_ru.json'
        with open(heroes_ru_json_file, encoding='utf-8') as heroes_ru_json:
            heroes_ru_list = json.load(heroes_ru_json)
        for hero, data in heroes_ru_list.items():
            if hero_name in bug_names:
                hero_name = bug_names[hero_name]
            if hero_name == data['name_en'] or hero_name == data['name_ru'] or hero_name == hero:
                self.id: str = data['name_id']
                self.en: str = data['name_en']
                self.ru: str = data['name_ru']
                self.json: str = data['name_json']
                self.role: str = data['role']
                self.tier: str = data['tier']
                self.nick: list = data['nick']

    def __repr__(self):
        return f'Hero({self.id})'

    def __str__(self):
        return self.id

    def __eq__(self, hero2):
        if self.id == hero2.id or \
                self.en == hero2.en or \
                self.ru == hero2.ru:
            return True
        else:
            return False

    def get_name_id(self):
        print('Возврат героя')
        return self.id

    def get_role(self):
        print('Возврат роли')
        return self.role
