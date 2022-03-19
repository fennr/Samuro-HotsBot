import requests
import psycopg2.extras
import itertools as it
from discord import Embed, utils, Member
from bs4 import BeautifulSoup
from utils.classes.Player import Player
from utils.classes.Stats import Stats
from utils.classes.Team import Team
from collections.abc import MutableMapping
from datetime import datetime
import utils
from utils import exceptions, sql, library

config = library.files.get_yaml()

leagues = {
    "Bronze": "Бронза",
    "Silver": "Серебро",
    "Gold": "Золото",
    "Platinum": "Платина",
    "Diamond": "Алмаз",
    "Master": "Мастер",
    "Grandmaster": "Грандмастер"
}

flatten_mmr = {
    'Bronze.5': 0, 'Bronze.4': 2250, 'Bronze.3': 2300, 'Bronze.2': 2350, 'Bronze.1': 2400,
    'Silver.5': 2450, 'Silver.4': 2470, 'Silver.3': 2490, 'Silver.2': 2510, 'Silver.1': 2530,
    'Gold.5': 2550, 'Gold.4': 2575, 'Gold.3': 2600, 'Gold.2': 2625, 'Gold.1': 2650,
    'Platinum.5': 2675, 'Platinum.4': 2695, 'Platinum.3': 2715, 'Platinum.2': 2735, 'Platinum.1': 2755,
    'Diamond.5': 2775, 'Diamond.4': 2800, 'Diamond.3': 2825, 'Diamond.2': 2850, 'Diamond.1': 2875,
    'Master.0': 2900, 'Grandmaster.0': 3100,
}

selects = {
    'PlayersIdOrBtag': 'SELECT * FROM "Players" WHERE id = %s OR btag = %s',
    'PlayersBtag': 'SELECT * FROM "Players" WHERE btag = %s',
    'PlayersInBtag': 'SELECT * FROM "Players" WHERE btag IN (%s)',
    'PlayersId': 'SELECT * FROM "Players" WHERE id = %s',
    'PlayersTeam': 'SELECT * FROM "Players" WHERE team = %s',
    'PlayersAll': 'SELECT * FROM "Players"',
    'hpAll': 'SELECT * FROM "heroesprofile"',
    'ehActive': 'SELECT * FROM "EventHistory" WHERE room_id = %s AND active = %s',
    'usIdGuild': 'SELECT * FROM "UserStats" WHERE id = %s AND guild_id = %s',
    'usAll': 'SELECT * FROM "UserStats"',
    'usGuild': 'SELECT * FROM "UserStats" WHERE guild_id = %s',
    'usPoints': 'SELECT * FROM "UserStats" WHERE guild_id = %s AND points > 0 ORDER BY points DESC LIMIT %s',
    'usWins': 'SELECT * FROM "UserStats" WHERE guild_id = %s AND win > 0 ORDER BY win DESC LIMIT %s',
    'teamName': 'SELECT * FROM "Teams" WHERE name = %s',
    'teamId': 'SELECT * FROM "Teams" WHERE id = %s',
    'teamLid': 'SELECT * FROM "Teams" WHERE leader = %s',
    'teamIdName': 'SELECT * FROM "Teams" WHERE id = %s or name = %s',
    'achievId': 'SELECT * FROM "Achievements" WHERE id = %s',
    'achievAll': 'SELECT * FROM "Achievements" WHERE guild_id = %s',
    'userAchiev': '''SELECT (ua.id, a.name, ua.date) FROM "UserAchievements" as ua
                    INNER JOIN "Achievements" as a
                    ON ua.achievement = a.id
                    WHERE ua.id = %s''',
    'PlayersLeague': '''SELECT p.* FROM "Players" as p
                        INNER JOIN "UserStats" as us
                        ON p.id = us.id AND p.guild_id = us.guild_id
                        WHERE league = %s ORDER BY mmr DESC LIMIT %s''',
}

deletes = {
    'PlayerIdOrBtag': 'DELETE FROM "Players" WHERE id = %s OR btag = %s',
    'PlayerId': 'DELETE FROM "Players" WHERE id = %s',
    'TeamLid': 'DELETE FROM "Teams" WHERE leader = %s',
    'UserAchiev': '''DELETE FROM "UserAchievements" 
                WHERE id = %s AND guild_id = %s AND achievement = %s''',
    'AchievId': 'DELETE FROM "Achievements" WHERE id = %s AND guild_id = %s RETURNING name',
}

inserts = {
    'Player': '''INSERT INTO "Players"(btag, id, guild_id, mmr, league, division)
                VALUES (%s, %s, %s, %s, %s, %s)''',
    'Team': '''INSERT INTO "Teams"(name, leader) 
                VALUES (%s, %s) RETURNING id''',
    'Achievement': '''INSERT INTO "Achievements"(guild_id, name) 
                VALUES (%s, %s) RETURNING id''',
    'UserAchiev': '''INSERT INTO "UserAchievements"(id, guild_id, achievement, date) 
                VALUES(%s, %s, %s, %s) '''
}

updates = {
    'PlayerMMR': 'UPDATE "Players" SET league = %s, division = %s, mmr = %s WHERE id=%s',
    'PlayerTeam': 'UPDATE "Players" SET team = %s WHERE id = %s',
    'TeamMembers': 'UPDATE "Teams" SET members = %s WHERE id = %s',
    'StatsPoints': 'Update "UserStats" SET points = %s WHERE id = %s AND guild_id = %s',
}


def team_change_stats(team: list, guild_id, delta=7, points=1, winner=True):
    con, cur = get_con_cur()
    placeholder = '%s'
    placeholders = ', '.join(placeholder for unused in team)
    select = selects.get('PlayersInBtag') % placeholders
    cur.execute(select, team)
    records = cur.fetchall()
    for record in records:
        player = get_player(record)
        select = selects.get('usIdGuild')
        cur.execute(select, (player.id, guild_id))
        stats_rec = cur.fetchone()
        if stats_rec is None:
            player_stats = Stats(player.id, guild_id, player.btag)
            insert = '''INSERT INTO "UserStats"(id, guild_id, win, lose, points, btag)
                                                    VALUES (%s, %s, %s, %s, %s, %s)'''
            cur.execute(insert, (player_stats.id, player_stats.guild_id, player_stats.win,
                                 player_stats.lose, player_stats.points, player_stats.btag))
        else:
            player_stats = Stats(id=stats_rec.id, guild_id=stats_rec.guild_id,
                                 btag=stats_rec.btag, win=stats_rec.win, lose=stats_rec.lose,
                                 points=stats_rec.points)
        if winner:
            player.mmr += int(delta)
            player_stats.points += int(points) + 2
            player_stats.win += 1
        else:
            player.mmr -= int(delta)
            player_stats.points += int(points)
            player_stats.lose += 1
        player.league, player.division = get_league_division_by_mmr(player.mmr)
        updateUS = '''UPDATE "UserStats" SET points = %s, win = %s, lose = %s 
                WHERE id = %s AND guild_id = %s'''
        updateP = '''UPDATE "Players" SET mmr = %s, league = %s, division = %s 
                WHERE id = %s and guild_id = %s'''
        cur.execute(updateUS, (player_stats.points, player_stats.win, player_stats.lose,
                               player_stats.id, player_stats.guild_id))
        cur.execute(updateP, (player.mmr, player.league, player.division,
                              player.id, player.guild_id))
        print(f"{player.btag} -> {player.mmr} mmr ({player.league})")
    commit(con)


def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.') -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + str(k) if parent_key else str(k)
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_league_division_by_mmr(mmr):
    league, division = next(
        x[1][0].split(sep='.') for x in enumerate(reversed(flatten_mmr.items())) if x[1][1] < mmr)
    return league, division


def get_likes(ctx):
    like = utils.get(ctx.guild.emojis, name="like")
    dislike = utils.get(ctx.guild.emojis, name="dislike")
    if like is None:
        like = '\N{THUMBS UP SIGN}'
        dislike = '\N{THUMBS DOWN SIGN}'
    return like, dislike


def min_diff_sets(data):
    """
        Parameters:
        - `data`: input list.
        Return:
        - min diff between sum of numbers in two sets
    """
    print(data)
    if len(data) == 1:
        return data[0]
    s = sum(data)
    # `a` is list of all possible combinations of all possible lengths (from 1
    # to len(data) )
    a = []
    for i in range(1, len(data)):
        a.extend(list(it.combinations(data, i)))
    # `b` is list of all possible pairs (combinations) of all elements from `a`
    b = it.combinations(a, 2)
    # `c` is going to be final correct list of combinations.
    # Let apply 2 filters:
    # 1. leave only pairs where: sum of all elements == sum(data)
    # 2. leave only pairs where: flat list from pairs == data
    c = filter(lambda x: sum(x[0]) + sum(x[1]) == s, b)
    c = filter(lambda x: sorted([i for sub in x for i in sub]) == sorted(data), c)
    # `res` = [min_diff_between_sum_of_numbers_in_two_sets,
    #           ((set_1), (set_2))
    #         ]
    print(c)
    res = sorted([(abs(sum(i[0]) - sum(i[1])), i) for i in c],
                 key=lambda x: x[0])
    # print(res)
    # return min([i[0] for i in res])
    min_mmr = min([i[0] for i in res])
    for i in res:
        if i[0] == min_mmr:
            red_team = i[1][0]
            blue_team = i[1][1]
            return red_team, blue_team


def profile_not_found(user):
    return f"Профиль {user} не найден в базе.\n" \
           f"Добавьте его командой #profile add батлтаг# @discord"


def get_heroesprofile_data(btag, user_id, guild_id):
    #print("get_data")
    bname = btag.replace('#', '%23')
    base_url = 'https://www.heroesprofile.com'
    url = 'https://www.heroesprofile.com/Search/?searched_battletag=' + bname
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246 '
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(url)
    error = soup.find('div', attrs={'id': 'choose_battletag'})
    if error is not None:
        links = error.find_all('a')
        for link in links:
            region = 'ion=2'
            if region in link['href']:
                url_new = base_url + link['href'].replace('®', '&reg')
                # print(url_new)
                response = requests.get(url_new, headers={"User-Agent": f"{user_agent}"})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

    mmr_container = soup.find('section', attrs={'class': 'mmr-container'})
    mmr_info = mmr_container.find_all('div', attrs={'class': 'league-element'})
    storm_flag = False
    for elem in mmr_info:
        if elem.h3.text == 'Storm League':
            storm_flag = True
            tags = elem.find_all('div')
            for tag in tags[:1]:
                profile_data = (" ".join(tag.text.split())).split()
                #print(profile_data)
                profile_wr = profile_data[2]
                if profile_data[3] == 'Master':
                    profile_league = profile_data[3]
                    profile_division = 0
                    profile_mmr = int(''.join([i for i in profile_data[5] if i.isdigit()]))
                else:
                    profile_league = profile_data[3]
                    profile_division = int(profile_data[4])
                    profile_mmr = int(''.join([i for i in profile_data[6] if i.isdigit()]))
                if profile_mmr < 2200:
                    profile_mmr = 2200
                return Player(btag=btag, id=user_id, guild_id=guild_id, mmr=profile_mmr, league=profile_league,
                              division=profile_division)
    if not storm_flag:
        raise exceptions.LeagueNotFound
    return None


def get_player_data(player: Player):
    return f"{get_discord_mention(player.id)} (*btag:* {player.btag}, *mmr:* {player.mmr})\n"


def get_user_id(member):
    return int(''.join([i for i in member if i.isdigit()]))


def get_discord_mention(id):
    return '<@' + str(id) + '>'


def get_player(record):
    if record is not None:
        player = Player(btag=record.btag, id=record.id, guild_id=record.guild_id,
                        mmr=record.mmr, league=record.league, division=record.division,
                        team=record.team)
        return player
    return None


def get_stats(record):
    if record is not None:
        stats = Stats(btag=record.btag, id=record.id, guild_id=record.guild_id,
                      win=record.win, lose=record.lose, points=record.points)
        return stats
    return None


def get_team(record):
    if record is not None:
        team = Team(id=record.id, name=record.name, leader=record.leader,
                    members=record.members, points=record.points)
        return team
    return None


def get_profile_by_id(id):
    sql.sql_init()
    con = sql.get_connect()
    cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    select = selects.get('PlayersId')
    cur.execute(select, (id,))
    record = cur.fetchone()
    player = get_player(record)
    return player, con, cur


def get_profile_by_id_or_btag(id_or_btag):
    con, cur = get_con_cur()
    user_id = get_user_id(id_or_btag)
    select = selects.get('PlayersIdOrBtag')
    cur.execute(select, (user_id, id_or_btag,))
    player = get_player(cur.fetchone())
    return player


def avatar(ctx, avamember: Member = None):
    return avamember.avatar_url


def check_user(ctx):
    user_id = get_author_id(ctx)
    con, cur = get_con_cur()
    select = selects.get('PlayersId')
    cur.execute(select, (user_id,))
    player = get_player(cur.fetchone())
    return player


def get_user_team_embed(embed, team_id):
    con, cur = get_con_cur()
    select = selects.get('teamId')
    cur.execute(select, (team_id,))
    team = get_team(cur.fetchone())
    embed.add_field(
        name="Команда",
        value=team.name,
        inline=True,
    )
    return embed


def get_team_embed(team: Team):
    con, cur = get_con_cur()
    embed = Embed(
        title=f"Команда {team.name} (id: {team.id})",
        color=config["info"]

    )
    embed.add_field(
        name="Лидер",
        value=f"<@{team.leader}>",
        inline=True,
    )
    if team.members > 1:
        select = selects.get("PlayersTeam")
        cur.execute(select, (team.id, ))
        records = cur.fetchall()
        teams = ''
        for record in records:
            player = get_player(record)
            teams += f'<@{player.id}> (btag: {player.btag}, mmr: {player.mmr})\n'
        embed.add_field(
            name="Команда",
            value=teams,
            inline=False
        )
    return embed


def get_stats_embed(embed, stats: Stats):
    embed.add_field(
        name="Баллов",
        value=stats.points,
        inline=True,
    )
    embed.add_field(
        name="Статистика внутренних турниров\n(побед/поражений)",
        value=f"{stats.win} / {stats.lose}",
        inline=False
    )
    return embed


def get_profile_embed(ctx, player: Player):
    embed = Embed(
        title=f"{player.btag}",
        color=config["info"]

    )
    if player.division:
        embed.add_field(
            name="Лига",
            value=f"{leagues.get(player.league)} {player.division}",
            inline=True
        )
    else:
        embed.add_field(
            name="Лига",
            value=leagues.get(player.league),
            inline=True
        )
    embed.add_field(
        name="ММР",
        value=player.mmr,
        inline=True
    )
    return embed


def get_achievements_embed(embed: Embed, player: Player):
    con, cur = get_con_cur()
    select = selects.get("userAchiev")
    cur.execute(select, (player.id, ))
    records = cur.fetchall()
    if cur.rowcount:
        achievements = ''
        for record in records:
            print(record.row)
            user_id, achiev_name, achiev_date = record.row[1:-1].split(",")
            date_obj = datetime.strptime(achiev_date, '%Y-%m-%d').date()
            date = date_obj.strftime('%d %B %Y')
            achievements += f"**{achiev_name}** - получено {date}\n"
        embed.add_field(
            name="Достижения",
            value=achievements,
            inline=False
        )
    return embed


def sort_by_mmr(player):
    return player.mmr


def change_mmr(player: Player, delta: int, plus=True):
    if plus:
        return player.mmr + delta
    else:
        return player.mmr - delta


def get_guild_id(ctx):
    if ctx.guild is None:
        guild_id = ''
    else:
        try:
            guild_id = ctx.message.guild.id
        except:
            guild_id = ctx.guild_id
    return guild_id


def get_author(ctx):
    try:
        author = ctx.author.name
    except:
        author = ctx.message.author.name
    return author


def get_author_id(ctx):
    try:
        author_id = ctx.message.author.id
    except:
        author_id = ctx.author.id
    return author_id


def get_con_cur():
    sql.sql_init()
    con = sql.get_connect()
    cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    return con, cur


def commit(con):
    con.commit()
    con.close()
