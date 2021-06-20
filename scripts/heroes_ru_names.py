import json
import os


def create_ru_list_heroes(filename):
    """
    Генерирует список героев на русском

    :param filename: Путь до файла
    :return: Список геров (list)
    """
    ru_heroes_list = []
    # heroes_txt = urlopen(filename.download_url).read()
    # heroes_txt = heroes_txt.decode('cp1251').splitlines()
    with open(filename, 'r', encoding='cp1251') as heroes_txt:
        for line in heroes_txt:
            if len(line) > 0:
                hero_ru, tail = line.split(sep='/', maxsplit=1)
                hero_en, tail = tail.split(sep=' — ', maxsplit=1)
                stlk_url, tail = tail.split(sep=' ', maxsplit=1)
                tail = tail[1:-2]
                shortbuild, hero_name = tail.split(sep=',')
                heroes = dict(name_ru=hero_ru, name_en=hero_en, name=hero_name, build=shortbuild, url=stlk_url)
                ru_heroes_list.append(heroes)

    return ru_heroes_list

def create_nick_list(filename):
    nick_list = []
    with open(filename, 'r', encoding='utf-8') as heroes_txt:
        for line in heroes_txt:
            if len(line) > 0:
                line = line.replace(' ', '').replace('\n', '')
                cHeroId, nick = line.split(sep=':', maxsplit=1)
                #print('{} {}'.format(cHeroId, nick))
                nicks = nick.split(',')
                nicks = [word.capitalize() for word in nicks]
                hero_nick = dict(cHeroId=cHeroId, nick=nicks)
                nick_list.append(hero_nick)
    return nick_list

def find_hero(hero_name):
    """
    Поиск героя по имени на русском или английском

    :param hero_name:Имя героя (string)
    :return: Имя героя (string)
    """
    #hero_name = hero_name.capitalize()
    stlk_file = 'data/stlk_builds.txt'
    heroes_list = create_ru_list_heroes(stlk_file)
    for hero in heroes_list:
        if (hero['name_ru'] == hero_name) or (hero['name'] == hero_name) or (hero['name_en'] == hero_name):
            return hero
    return None



def find_nick(hero_name):
    nicknames_file = 'data/hero_nicks.txt'
    nick_list = create_nick_list(nicknames_file)
    for hero in nick_list:
        if hero['cHeroId'] == hero_name:
            return hero
    return None


def create_heroes_ru_data():
    full_dict = {}
    tree = os.walk('hero')

    heroes_json_file = 'data/heroesdata_ru.json'
    f = open(heroes_json_file, 'w')
    f.close()

    nicknames_file = 'data/hero_nicks.txt'
    '''
    f = open(nicknames_file, 'w')
    f.close()
    '''

    heroes_json_list = list(tree)[0][2]
    #print(heroes_json_list)
    count = 0
    nick_list = create_nick_list(nicknames_file)
    #print(nick_list)
    for hero_json in heroes_json_list:
        hero_dict = {}
        if count < 150:
            path = 'hero/' + hero_json
            with open(path, 'r') as read_file:
                hero_data = json.load(read_file)
            count += 1
            '''with open(nicknames_file, 'a', encoding='utf-8') as file_nicks:
                file_nicks.write(hero_data['cHeroId'] + ':\n')'''
            hero_nick = find_nick(hero_data['cHeroId'])
            try:
                hero = find_hero(hero_data['cHeroId'])
                hero_dict = dict(name_en=hero_data['name'], name_ru=hero['name_ru'].replace("`", ''), nick=hero_nick['nick'])
            except:
                try:
                    hero = find_hero(hero_data['name'])
                    hero_dict = dict(name_en=hero_data['name'], name_ru=hero['name_ru'].replace("`", ''), nick=[])
                except:
                    try:
                        hero = find_hero(hero_data['hyperlinkId'])
                        hero_dict = dict(name_en=hero_data['name'], name_ru=hero['name_ru'].replace("`", ''), nick=[])
                    except:
                        print('{}, {}, {}'.format(hero_data['cHeroId'], hero_data['name'], hero_data['hyperlinkId'] ))
                        #print(hero)
                        hero_dict = dict(name_en=hero_data['name'], name_ru='Error', nick=[])

            full_dict[hero_data['cHeroId']] = hero_dict

    with open(heroes_json_file, 'w', encoding='utf-8') as result_file:
        json.dump(full_dict, result_file, ensure_ascii=False, indent=4)
    print('File with Heroes was created')


if __name__ == '__main__':
    create_heroes_ru_data()