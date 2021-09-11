import psycopg2
import datetime
import pytz
from hots.function import find_heroes, read_hero_from_message
from hots.Hero import Hero


if __name__ == '__main__':
    data_type_day = '%d %B'
    data_type_time = '%H:%M'
    data_type = data_type_day + data_type_time
    timezone = 'Europe/Moscow'
    now = datetime.datetime.now(pytz.timezone(timezone)).strftime(data_type)
    #now = datetime.datetime.strptime(datetime.datetime.today().strftime(data_type), data_type) \
    #    .replace(year=datetime.datetime.now().year) + datetime.timedelta(hours=3)
    print(now)
