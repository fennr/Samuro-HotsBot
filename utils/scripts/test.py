from collections.abc import MutableMapping
from utils.library import profile as pl
from utils.classes.Stats import Stats
from utils.scripts.ytparser import *
from pprint import pprint
import os
import stackprinter
import trovoApi

c = trovoApi.TrovoClient("9637368b14df5d39619fc6e4af4a79ec")
stackprinter.set_excepthook(style='darkbg2')

mmr = {
    "Bronze": {
        5: 0,
        4: 2250,
        3: 2300,
        2: 2350,
        1: 2400
    },
    "Silver": {
        5: 2450,
        4: 2470,
        3: 2490,
        2: 2510,
        1: 2530
    },
    "Gold": {
        5: 2550,
        4: 2575,
        3: 2600,
        2: 2625,
        1: 2650
    },
    "Platinum": {
        5: 2675,
        4: 2695,
        3: 2715,
        2: 2735,
        1: 2755
    },
    "Diamond": {
        5: 2775,
        4: 2800,
        3: 2825,
        2: 2850,
        1: 2875
    },
    "Master": {
        0: 2900
    }
}

flatten_mmr = {
    'Bronze.5': 0, 'Bronze.4': 2250, 'Bronze.3': 2300, 'Bronze.2': 2350, 'Bronze.1': 2400,
    'Silver.5': 2450, 'Silver.4': 2470, 'Silver.3': 2490, 'Silver.2': 2510, 'Silver.1': 2530,
    'Gold.5': 2550, 'Gold.4': 2575, 'Gold.3': 2600, 'Gold.2': 2625, 'Gold.1': 2650,
    'Platinum.5': 2675, 'Platinum.4': 2695, 'Platinum.3': 2715, 'Platinum.2': 2735, 'Platinum.1': 2755,
    'Diamond.5': 2775, 'Diamond.4': 2800, 'Diamond.3': 2825, 'Diamond.2': 2850, 'Diamond.1': 2875,
    'Master.0': 2900,
}



def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str ='.') -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + str(k) if parent_key else str(k)
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def test(player_mmr):
    league, division = next(x[1][0].split(sep='.') for x in enumerate(reversed(flatten_mmr.items())) if x[1][1] < player_mmr)
    return league, division


def test_list():
    con, cur = pl.get_con_cur()
    guild_id = 845658540341592096
    user_id = ['Se7eN#22874', 'ckboroff#2186']
    placeholder = '%s'
    placeholders = ', '.join(placeholder for unused in user_id)
    select = pl.selects.get('PlayersBtag') % placeholders
    print(select)
    cur.execute(select, user_id)
    records = cur.fetchall()
    for record in records:
        select = 'SELECT * FROM "UserStats" WHERE id = %s'
        cur.execute(select, (record.id, ))
        stats_rec = cur.fetchone()
        if stats_rec is None:
            stats_rec = Stats(id=record.id, btag=record.btag, guild_id=guild_id)
            insert = '''INSERT INTO "UserStats"(id, guild_id, win, lose, points, btag)
                                        VALUES (%s, %s, %s, %s, %s, %s)'''
            cur.execute(insert, (record.id, guild_id, 0, 0, 0 , record.btag))
        print(stats_rec)

def test_changemmr():
    team = ['Se7eN#22874', 'ckboroff#2186']
    guild_id = 845658540341592096
    pl.team_change_stats(team, guild_id, winner=False)


def test_team():
    con, cur = pl.get_con_cur()
    select = pl.selects.get('teamId')
    cur.execute(select, (15, ))
    record = cur.fetchone()
    print(record)
    team = pl.get_team(record)
    print(team)

def test_ytparser():
    yt_data("AIzaSyAo-D35Tct18rJPqtiYv17QGS-bHhQBBo4", "PanchoProduction")
    return "Запись данных завершена"

def get_video():
    data = get_last_videos(os.environ.get('YT_API'), "PanchoProduction")
    return data

def do_stuff():
    raise ValueError('Error message')



if __name__ == '__main__':
    pprint(c.get_top_channels(limit=10, category_id='10265')['top_channels_lists'])

