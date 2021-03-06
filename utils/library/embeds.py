from datetime import datetime

from discord import Embed
from utils.classes import Hero, Const, Player, Stats, Team
from utils import config, library
from utils.library import leagues


def add_thumbnail(hero: Hero, embed):
    ext = '.png'
    thumb_url = 'https://nexuscompendium.com/images/portraits/'
    hero_name = hero.en.lower().replace('.', '').replace("'", "").replace(' ', '-')
    url = thumb_url + hero_name + ext
    embed.set_thumbnail(
        url=url
    )
    return embed


def profile(ctx, player: Player):
    embed = Embed(
        title=f"{player.btag}",
        color=config.info

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


def achievements(ctx, embed: Embed, player: Player):
    con, cur = library.get.con_cur()
    guild_id = library.get.guild_id(ctx)
    select = Const.selects.UserAchiev
    cur.execute(select, (player.id, guild_id))
    records = cur.fetchall()
    if cur.rowcount:
        achievements = ''
        for record in records:
            #print(record.row)
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


def stats(embed: Embed, stats: Stats) -> Embed:
    if stats.win + stats.lose > 0:
        embed.add_field(
            name="Баллы",
            value=stats.points,
            inline=True,
        )
        all = stats.win + stats.lose
        rate = round(stats.win / all * 100)
        embed.add_field(
            name="Винрейт 5х5",
            value=f"{rate}% ({stats.win} из {all})",
            inline=True
        )
    if stats.winstreak > 2:
        embed.add_field(
            name="Винстрик",
            value=f"{stats.winstreak} (best: {stats.max_ws})",
            inline=True
        )
    return embed


def votes(embed, player):
    con, cur = library.get.con_cur()
    select = Const.selects.VoteStatsId
    cur.execute(select, (player.id, ))
    record = cur.fetchone()
    #print(record)
    if record is not None:
        if record.correct + record. wrong > 0:
            all = record.correct + record.wrong
            rate = round(record.correct / all * 100)
            embed.add_field(
                name="Ставки",
                value=f"{rate}% ({record.correct} из {all})",
                inline=True
            )
    return embed


def team(team: Team) -> Embed:
    con, cur = library.get.con_cur()
    embed = Embed(
        title=f"Команда {team.name}",
        color=config.info

    )
    select = Const.selects.PlayersId
    cur.execute(select, (team.leader, ))
    leader = library.get.player(cur.fetchone())
    embed.add_field(
        name="Лидер",
        value=f"{library.get.mention(leader.id)} (btag: {leader.btag}, mmr: {leader.mmr})",
        inline=True,
    )
    if team.members > 1:
        select = Const.selects.PlayersTeam
        cur.execute(select, (team.id,))
        records = cur.fetchall()
        teams = ''
        for record in records:
            player = library.get.player(record)
            if player.id != team.leader:
                teams += f'{library.get.mention(player.id)} (btag: {player.btag}, mmr: {player.mmr})\n'
        embed.add_field(
            name="Команда",
            value=teams,
            inline=False
        )
    return embed


def user_team(embed: Embed, team_id: int) -> Embed:
    con, cur = library.get.con_cur()
    select = Const.selects.TeamId
    cur.execute(select, (team_id,))
    team = library.get.team(cur.fetchone())
    embed.add_field(
        name="Команда",
        value=team.name,
        inline=True,
    )
    return embed
