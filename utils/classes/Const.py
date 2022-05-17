import json
from dataclasses import dataclass
from utils.library import files
from enum import Enum

conf = files.get_yaml("config.yaml")

black_list = files.black_list()


@dataclass(frozen=True)
class Config:
    bot_initial_prefix: list  # содержит несколько префиксов на которые бот отзывается
    bot_prefix: str           # префикс выводящийся во всех справках как основной
    patch: str
    short_patch: str
    log: str
    version: str
    update: str
    owners: list              # на случай если требуется несколько людей с суперправами
    admins: list
    main_color: int
    error: int
    success: int
    warning: int
    info: int
    grey: int


@dataclass(frozen=True)
class FileName:
    config: str
    gamestrings: str
    heroes: str
    heroes_ru: str
    pancho: str
    stlk: str


@dataclass(frozen=True)
class Json:
    heroes: dict
    heroes_ru: dict
    gamestrings: dict
    pancho: dict
    stlk: dict


@dataclass(frozen=True)
class Select:
    PlayersIdOrBtag: str
    PlayersBtag: str
    PlayersInBtag: str
    PlayersId: str
    PlayersTeam: str
    Players: str
    HP: str
    HPBtag: str
    EHActive: str
    USIdGuild: str
    US: str
    USGuild: str
    USGuildAll: str
    USPoints: str
    USWins: str
    TeamName: str
    TeamId: str
    TeamLid: str
    TeamIdName: str
    AchievGuild: str
    AchievId: str
    UserAchiev: str
    PlayersLeague: str
    VotesEvent: str
    VoteStatsId: str
    BlackList: str


@dataclass(frozen=True)
class Update:
    PlayerMMR: str
    PlayerTeam: str
    TeamMembers: str
    USPoints: str
    USPointWinLoseWinStr: str
    EHWinner: str
    USGuildRemoveStats: str


@dataclass(frozen=True)
class Delete:
    PlayerIdOrBtag: str
    PlayerId: str
    TeamLid: str
    UserAchiev: str
    AchievId: str
    EventActive: str
    BlackList: str


@dataclass(frozen=True)
class Insert:
    Player: str
    Team: str
    Achievement: str
    UserAchiev: str
    UserStats: str
    Event: str
    Votes: str
    BlackList: str


@dataclass(frozen=True)
class Event:
    role: str
    blue: str
    red: str
    role_id: int

config = Config(
    bot_initial_prefix=conf["bot_initial_prefix"],
    bot_prefix=conf["bot_prefix"],
    patch=conf["patch"],
    short_patch=conf["patch"][-5:],
    log=conf["log"],
    version=conf["version"],
    update=conf["update"],
    owners=conf["owners"],
    admins=conf["admins"],
    main_color=conf["main_color"],
    error=conf["error"],
    success=conf["success"],
    warning=conf["warning"],
    info=conf["info"],
    grey=conf["grey"],
)


data = FileName(
    config="config.yaml",
    gamestrings=f"data/gamestrings/gamestrings_{config.short_patch}_ruru.json",
    heroes=f"data/heroesdata_{config.short_patch}.json",
    heroes_ru=f"data/heroesdata_ru.json",
    pancho=f"data/pancho.json",
    stlk=f"data/stlk_builds.json"
)

jsons = Json(
    heroes=files.get_json(data.heroes),
    heroes_ru=files.get_json(data.heroes_ru),
    gamestrings=files.get_json(data.gamestrings),
    pancho=files.get_json(data.pancho),
    stlk=files.get_json(data.stlk)
)

flatten_mmr = {
    'Bronze.5': 0, 'Bronze.4': 2250, 'Bronze.3': 2300, 'Bronze.2': 2350, 'Bronze.1': 2400,
    'Silver.5': 2450, 'Silver.4': 2470, 'Silver.3': 2490, 'Silver.2': 2510, 'Silver.1': 2530,
    'Gold.5': 2550, 'Gold.4': 2575, 'Gold.3': 2600, 'Gold.2': 2625, 'Gold.1': 2650,
    'Platinum.5': 2675, 'Platinum.4': 2695, 'Platinum.3': 2715, 'Platinum.2': 2735, 'Platinum.1': 2755,
    'Diamond.5': 2775, 'Diamond.4': 2800, 'Diamond.3': 2825, 'Diamond.2': 2850, 'Diamond.1': 2875,
    'Master.0': 2900, 'Grandmaster.0': 3100,
}

selects = Select(
    PlayersIdOrBtag='SELECT * FROM "Players" WHERE id = %s OR btag = %s',
    PlayersId='SELECT * FROM "Players" WHERE id = %s',
    PlayersBtag='SELECT * FROM "Players" WHERE btag = %s',
    PlayersInBtag='SELECT * FROM "Players" WHERE btag IN (%s)',
    PlayersTeam='SELECT * FROM "Players" WHERE team = %s',
    Players='SELECT * FROM "Players"',
    HP='SELECT * FROM "heroesprofile"',
    HPBtag="""SELECT * FROM heroesprofile WHERE btag = %s""",
    EHActive='SELECT * FROM "EventHistory" WHERE room_id = %s AND active = %s',
    USIdGuild='SELECT * FROM "UserStats" WHERE id = %s AND guild_id = %s',
    US='SELECT * FROM "UserStats"',
    USGuildAll= 'SELECT * FROM "UserStats" WHERE guild_id = %s',
    USGuild='SELECT * FROM "UserStats" WHERE id = %s AND guild_id = %s',
    USPoints='SELECT * FROM "UserStats" WHERE guild_id = %s AND points > 0 ORDER BY points DESC LIMIT %s',
    USWins='SELECT * FROM "UserStats" WHERE guild_id = %s AND win > 0 ORDER BY win DESC LIMIT %s',
    TeamName='SELECT * FROM "Teams" WHERE name = %s',
    TeamId='SELECT * FROM "Teams" WHERE id = %s',
    TeamLid='SELECT * FROM "Teams" WHERE leader = %s',
    TeamIdName='SELECT * FROM "Teams" WHERE id = %s or name = %s',
    AchievGuild='SELECT * FROM "Achievements" WHERE guild_id = %s',
    AchievId='SELECT * FROM "Achievements" WHERE id = %s',
    UserAchiev='''SELECT (ua.id, a.name, ua.date) FROM "UserAchievements" as ua
                    INNER JOIN "Achievements" as a
                    ON ua.achievement = a.id
                    WHERE ua.id = %s AND ua.guild_id = %s''',
    PlayersLeague='''SELECT p.* FROM "Players" as p
                        INNER JOIN "UserStats" as us
                        ON p.id = us.id AND p.guild_id = us.guild_id
                        WHERE league = %s ORDER BY mmr DESC LIMIT %s''',
    VotesEvent='''SELECT * FROM "Votes" WHERE event_id = %s''',
    VoteStatsId='''SELECT * FROM "VoteStats" WHERE id = %s''',
    BlackList='''SELECT * FROM "BlackList"'''

)

deletes = Delete(
    PlayerIdOrBtag='DELETE FROM "Players" WHERE id = %s OR btag = %s',
    PlayerId='DELETE FROM "Players" WHERE id = %s',
    TeamLid='DELETE FROM "Teams" WHERE leader = %s',
    UserAchiev='''DELETE FROM "UserAchievements" 
                WHERE id = %s AND guild_id = %s AND achievement = %s''',
    AchievId='DELETE FROM "Achievements" WHERE id = %s AND guild_id = %s RETURNING name',
    EventActive='''DELETE FROM "EventHistory" WHERE room_id = %s AND active = %s
                   RETURNING blue1, blue2, blue3, blue4, blue5,
                             red1, red2, red3, red4, red5''',
    BlackList='''DELETE FROM "BlackList" WHERE id = %s''',
)

inserts = Insert(
    Player='''INSERT INTO "Players"(btag, id, guild_id, mmr, league, division)
                VALUES (%s, %s, %s, %s, %s, %s)''',
    Team='''INSERT INTO "Teams"(name, leader) 
                VALUES (%s, %s) RETURNING id''',
    Achievement='''INSERT INTO "Achievements"(guild_id, name)
                VALUES (%s, %s) RETURNING id''',
    UserAchiev='''INSERT INTO "UserAchievements"(id, guild_id, achievement, date)
                VALUES(%s, %s, %s, %s) ''',
    UserStats='''INSERT INTO "UserStats"(id, guild_id, win, lose, points, btag)
                 VALUES (%s, %s, %s, %s, %s, %s)''',
    Event='''INSERT INTO "EventHistory"(time, admin, guild_id, active, room_id, type,
                    blue1, blue2, blue3, blue4, blue5, 
                    red1, red2, red3, red4, red5)
                    VALUES (%s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s )''',
    Votes='''INSERT INTO "Votes"(id, event_id, vote) VALUES (%s, %s, %s)''',
    BlackList='''INSERT INTO "BlackList"(id, name, reason) VALUES (%s, %s, %s)''',
)

updates = Update(
    PlayerMMR='UPDATE "Players" SET mmr = %s, league = %s, division = %s WHERE id=%s',
    PlayerTeam='UPDATE "Players" SET team = %s WHERE id = %s',
    TeamMembers='UPDATE "Teams" SET members = %s WHERE id = %s',
    USPoints='Update "UserStats" SET points = %s WHERE id = %s AND guild_id = %s',
    USPointWinLoseWinStr='''UPDATE "UserStats" SET 
                            points = %s, win = %s, lose = %s, 
                            winstreak = %s, max_ws = %s 
                            WHERE id = %s AND guild_id = %s''',
    EHWinner='''UPDATE "EventHistory" SET winner = %s, delta_mmr = %s, points = %s, active = %s 
                WHERE room_id = %s AND active = %s''',
    USGuildRemoveStats='''UPDATE "UserStats" SET win = 0, lose = 0, winstreak = 0
                          WHERE guild_id = %s AND points < 10''',

)

events = Event(
    role='5x5 player',
    role_id=957359993261281290,  # роль 5x5
    blue='blue',
    red='red',
)

class League(Enum):
    Bronze = "Бронза"
    Silver = "Серебро"
    Gold = "Золото"
    Platinum = "Платина"
    Diamond = "Алмаз"
    Master = "Мастер"
    Grandmaster = "Грандмастер"
