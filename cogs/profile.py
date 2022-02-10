import os
import sys

from discord import Embed, utils
import yaml
import psycopg2.extras
from discord.ext import commands
from helpers import sql
import requests
from bs4 import BeautifulSoup
from hots.Player import Player
from statistics import mean

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


def get_heroesprofile_data(btag, discord_name):
    bname = btag.replace('#', '%23')
    base_url = 'https://www.heroesprofile.com'
    url = 'https://www.heroesprofile.com/Search/?searched_battletag=' + bname
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    error = soup.find('div', attrs={'id': 'choose_battletag'})
    if error is not None:
        links = error.find_all('a')
        for link in links:
            region = 'ion=2'
            if region in link['href']:
                url_new = base_url + link['href'].replace('®', '&reg')
        print(url_new)
        response = requests.get(url_new, headers={"User-Agent": f"{user_agent}"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

    mmr_container = soup.find('section', attrs={'class': 'mmr-container'})
    mmr_info = mmr_container.find_all('div', attrs={'class': 'league-element'})
    for elem in mmr_info:
        if elem.h3.text == 'Storm League':
            tags = elem.find_all('div')
            for tag in tags[:1]:
                profile_data = (" ".join(tag.text.split())).split()
                profile_wr = profile_data[2]
                if profile_data[3] == 'Master':
                    profile_league = profile_data[3]
                    profile_division = '0'
                    profile_mmr = profile_data[5]
                else:
                    profile_league = profile_data[3]
                    profile_division = profile_data[4]
                    profile_mmr = profile_data[6]
                return Player(btag=btag, discord=discord_name, mmr=profile_mmr, league=profile_league,
                              division=profile_division, winrate=profile_wr)
    return None


def get_player(record):
    if record is not None:
        player = Player(btag=record.btag, discord=record.discord, mmr=record.mmr, league=record.rank,
                        division=record.division, winrate=record.winrate)
        return player
    return None


def get_profile_embed(player: Player):
    embed = Embed(
        title=f"Профиль игрока {player.btag}",
        color=config["info"]

    )
    embed.add_field(
        name="Лига",
        value=player.league,
        inline=True
    )
    embed.add_field(
        name="ММР",
        value=player.mmr,
        inline=True
    )
    return embed


def sort_by_mmr(player):
    return player.mmr


class Profile(commands.Cog, name="profile"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="event")
    async def event(self, ctx):
        """
        - Команды на основе базы профилей
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Для подбора команд используйте команду #event 5x5')

    @event.command(name="5x5")
    async def event_5x5(self, ctx, *args):
        if len(args) % 2:
            await ctx.send("Введите четное участников турнира")
        else:
            sql.sql_init()
            con = sql.get_connect()
            cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            players = []
            bad_flag = False
            for name in args:
                select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
                cur.execute(select, (name, name,))
                record = cur.fetchone()
                if record is not None:
                    player = get_player(record)
                    players.append(player)
                else:
                    bad_flag = True
                    await ctx.send(f"Участника {name} нет в базе")
            if not bad_flag:
                players.sort(key=sort_by_mmr, reverse=True)
                team_one = ' '.join([player.discord for index, player in enumerate(players) if index % 2])
                team_one_avg = mean([int(player.mmr) for index, player in enumerate(players) if index % 2])

                team_two = ' '.join([player.discord for index, player in enumerate(players) if not index % 2])
                team_two_avg = mean([int(player.mmr) for index, player in enumerate(players) if not index % 2])

                await ctx.send(f"Синяя команда (avg mmr = {team_one_avg:.2f}): {team_one}")
                await ctx.send(f"Красная команда (avg mmr = {team_two_avg:.2f}): {team_two}")


    @commands.group(name="profile")
    async def profile(self, ctx):
        """
        - Связь батлтега и дискорд профиля
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Для добавления игрока используйте команду #profile add батлтег дискорд\n '
                           'Пример: *#profile add player#1234 @player*')

    @profile.command(name="test")
    async def profile_test(self, ctx, *args):
        pass

    @profile.command(name="divisions")
    async def profile_divisions(self, ctx):
        if ctx.message.author.id in config["owners"]:
            sql.sql_init()
            con = sql.get_connect()
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            select = """SELECT * FROM heroesprofile"""
            cur.execute(select)
            rec = cur.fetchall()
            for player_list in rec:
                player = Player(btag=player_list['btag'], league=player_list['rank'], division='',
                                discord=player_list['discord'],
                                mmr=player_list['mmr'], winrate=player_list['winrate'])
                if player.league[-1].isdigit():
                    if player.league == 'Master':
                        division = 0
                    else:
                        division = player.league[-1]
                        player.league = player.league[:-1]
                    print(f"{player.league} {division}")
                    update = """UPDATE heroesprofile SET rank=%s, division=%s WHERE btag=%s"""
                    cur.execute(update, (player.league, division, player.btag))
            con.commit()
            con.close()
            await ctx.send("Записи были разделены на дивизионы")
        else:
            await ctx.send("Нет прав на выполнение команды")

    @profile.command(name="add")
    async def profile_add(self, ctx, btag, discord_user):
        print("profile_add")
        data = None
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor()
        select = """SELECT * FROM heroesprofile WHERE btag = %s"""
        cur.execute(select, (btag,))
        record = cur.fetchone()
        print(record)
        if record is not None and record[4] is None:
            cur.execute("""UPDATE heroesprofile SET discord=%s WHERE btag=%s""", (discord_user, btag))
            con.commit()
            await ctx.send(f"В запись пользователя {btag} добавлен дискорд профиль")
            con.close()
        if record is None:
            try:
                data = get_heroesprofile_data(btag, discord_user)
                insert = """INSERT INTO heroesprofile(BTAG, RANK, DIVISION, WINRATE, MMR, DISCORD) 
                            VALUES(%s, %s, %s, %s, %s, %s )"""
                cur.execute(insert, (data.btag, data.league, data.division, data.winrate, data.mmr, data.discord))
                con.commit()
                con.close()
                await ctx.send(f"Профиль игрока {btag} добавлен в базу")
            except:
                await ctx.send(f'Профиль игрока {btag} не найден')

    @profile.command(name="remove")
    async def profile_remove(self, ctx, user_or_btag):
        if ctx.message.author.id in config["owners"]:
            sql.sql_init()
            con = sql.get_connect()
            cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            delete = """DELETE FROM heroesprofile WHERE discord = %s OR btag = %s"""
            cur.execute(delete, (user_or_btag, user_or_btag,))
            con.commit()
            con.close()
            await ctx.send(f"Профиль {user_or_btag} удален из базы")
        else:
            await ctx.send("Нет прав на выполнение команды")

    @profile.command(name="update")
    async def profile_update(self, ctx, user_or_btag):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(select, (user_or_btag, user_or_btag,))
        record = cur.fetchone()
        if record is not None:
            player = get_player(record)
            print(player)
            try:
                data = get_heroesprofile_data(player.btag, player.discord)
                update = """UPDATE heroesprofile SET RANK=%s, WINRATE=%s, MMR=%s WHERE btag=%s"""
                cur.execute(update, (data.league, data.winrate, data.mmr, data.btag))
                con.commit()
                con.close()
                await ctx.send(f"Профиль игрока {player.btag} обновлен")
            except:
                await ctx.send(f'Профиль игрока {player.btag} не найден')
        else:
            await ctx.send(f"Профиль {user_or_btag} не найден в базе. Добавьте его командой #profile add")

    @profile.command(name="info")
    async def profile_info(self, ctx, user_or_btag):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(select, (user_or_btag, user_or_btag,))
        record = cur.fetchone()
        if record is not None:
            player = get_player(record)
            print(player)
            if player is not None:
                embed = get_profile_embed(player)
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"Профиль {user_or_btag} не найден в базе. Добавьте его командой #profile add")
        con.close()

    @profile.error
    @profile_add.error
    async def profile_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Не хватает аргументов. Необходимо указать батлтег и дискорд профиль\n"
                           "Пример: *#profile add player#1234 @player*")


def setup(bot):
    bot.add_cog(Profile(bot))
