import psycopg2
import datetime
from hots.function import find_heroes
from hots.Hero import Hero


if __name__ == '__main__':
    hero_list = find_heroes('Сомуро')
    #hero = Hero('Самуро')
    #print(hero.ru)
