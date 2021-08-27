from hots.function import find_heroes


from hots.Hero import Hero

if __name__ == '__main__':
    hero_name = 'Самуро'
    hero_list = find_heroes(hero_name)
    if len(hero_list) == 1:
        hero_name = hero_list[0]['name_id']
        hero = Hero(hero_name)

    hero_name2 = 'Назибо'
    hero_list = find_heroes(hero_name2)
    if len(hero_list) == 1:
        hero_name2 = hero_list[0]['name_id']
        hero2 = Hero(hero_name2)

    print(hero.name_id, hero2.name_id)
    print(hero)
    print(hero == hero2)
