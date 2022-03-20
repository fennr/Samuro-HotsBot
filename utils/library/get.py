from discord import utils
import psycopg2.extras
from utils import classes, sql
from utils.classes import Const


def con_cur():
    sql.sql_init()
    con = sql.get_connect()
    cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    return con, cur


def author(ctx) -> str:
    try:
        return ctx.message.author.name
    except AttributeError:
        return ctx.author


def author_id(ctx) -> int:
    try:
        return ctx.message.author.id
    except AttributeError:
        return ctx.author_id


def guild_name(ctx) -> str:
    if ctx.guild is None:
        return ''
    else:
        try:
            return ctx.guild.name
        except AttributeError:
            return ctx.guild


def guild_id(ctx) -> int:
    if ctx.guild is None:
        return ''
    else:
        try:
            return ctx.message.guild.id
        except AttributeError:
            return ctx.guild_id


def league_division_by_mmr(mmr):
    league, division = next(
        x[1][0].split(sep='.') for x in enumerate(reversed(Const.flatten_mmr.items())) if x[1][1] < mmr)
    return league, division


def likes(ctx):
    like = utils.get(ctx.guild.emojis, name="like")
    dislike = utils.get(ctx.guild.emojis, name="dislike")
    if like is None:
        like = '\N{THUMBS UP SIGN}'
        dislike = '\N{THUMBS DOWN SIGN}'
    return like, dislike


def user_id(member):
    return int(''.join([i for i in member if i.isdigit()]))


def mention(discord_id: int) -> str:
    return '<@' + str(discord_id) + '>'


def player_data(pl: classes.Player) -> str:
    return f"{mention(pl.id)} (*btag:* {pl.btag}, *mmr:* {pl.mmr})\n"


def player(record):
    if record is not None:
        return classes.Player(btag=record.btag, id=record.id, guild_id=record.guild_id,
                              mmr=record.mmr, league=record.league, division=record.division,
                              team=record.team)
    return None


def stats(record):
    if record is not None:
        return classes.Stats(btag=record.btag, id=record.id, guild_id=record.guild_id,
                             win=record.win, lose=record.lose, points=record.points)
    return None

def team(record):
    if record is not None:
        return classes.Team(id=record.id, name=record.name, leader=record.leader,
                            members=record.members, points=record.points)
    return None


def profile_by_id_or_btag(id_or_btag) -> classes.Player:
    con, cur = con_cur()
    player_id = user_id(id_or_btag)
    select = Const.selects.PlayersIdOrBtag
    cur.execute(select, (player_id, id_or_btag,))
    pl = player(cur.fetchone())
    return pl

