import psycopg2
import datetime
from hots.function import find_heroes, read_hero_from_message
from hots.Hero import Hero


if __name__ == '__main__':
    hero = read_hero_from_message((('Сомуро'),), 'fenrir')
    print(hero)
