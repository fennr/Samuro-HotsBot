import os
import sys
import requests
import yaml
import psycopg2.extras
import itertools as it
import pytz
import exceptions
from datetime import datetime
from discord import Embed, utils, Member
from discord.ext import commands
from helpers import sql, check
from bs4 import BeautifulSoup
from hots.Player import Player
from statistics import mean

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


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
    return f"Профиль {user} не найден в базе. Добавьте его командой #profile add батлтаг# @discord"


def get_heroesprofile_data(btag, discord_name):
    print("get_data")
    bname = btag.replace('#', '%23')
    base_url = 'https://www.heroesprofile.com'
    url = 'https://www.heroesprofile.com/Search/?searched_battletag=' + bname
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246 '
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    print(url)
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
                print(profile_data)
                profile_wr = profile_data[2]
                if profile_data[3] == 'Master':
                    profile_league = profile_data[3]
                    profile_division = '0'
                    profile_mmr = profile_data[5]
                else:
                    profile_league = profile_data[3]
                    profile_division = profile_data[4]
                    profile_mmr = ''.join([i for i in profile_data[6] if i.isdigit()])
                return Player(btag=btag, discord=discord_name, mmr=profile_mmr, league=profile_league,
                              division=profile_division, winrate=profile_wr, win=0, lose=0, search=False)
    return None


def get_player_data(player: Player):
    return f"{get_discord_mention(player.discord)} (*btag:* {player.btag}, *mmr:* {player.mmr})\n"


def get_discord_id(member):
    return ''.join([i for i in member if i.isdigit()])


def get_discord_mention(id):
    return '<@' + id + '>'


def get_player(record):
    if record is not None:
        player = Player(btag=record.btag, discord=record.discord, mmr=record.mmr, league=record.rank,
                        division=record.division, win=record.win, lose=record.lose, winrate=record.winrate,
                        search=record.search)
        return player
    return None


def get_profile_by_discord(id):
    sql.sql_init()
    con = sql.get_connect()
    cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    select = """SELECT * FROM heroesprofile WHERE discord = %s"""
    cur.execute(select, (id, ))
    record = cur.fetchone()
    player = get_player(record)
    return player, con, cur


def avatar(ctx, avamember: Member = None):
    return avamember.avatar_url


def get_profile_embed(player: Player):
    embed = Embed(
        title=f"{player.btag}",
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
    if player.win != 0 or player.lose != 0:
        embed.add_field(
            name="Участие во внутренних турнирах\n(побед/поражений)",
            value=f"{player.win} / {player.lose}",
            inline=False
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
            await ctx.send('Для подбора команд используйте команду #event 5x5 @10_профилей')

    @event.command(name="test")
    @check.is_admin()
    async def event_test(self, ctx, *, avamember: Member = None):
        await ctx.send('Тест прав на ивенты пройден')

    @event.command(name="5x5")
    @check.is_admin()
    async def event_5x5(self, ctx, *args):
        if len(args) != 10:
            await ctx.send("Введите 10 участников турнира")
        else:
            sql.sql_init()
            con = sql.get_connect()
            cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            players = []
            bad_flag = False
            for name in args:
                member = get_discord_id(name)
                select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
                cur.execute(select, (member, name,))
                record = cur.fetchone()
                if record is not None:
                    player = get_player(record)
                    players.append(player)
                else:
                    bad_flag = True
                    await ctx.send(f"Участника {name} нет в базе")
            if not bad_flag:
                select = """SELECT time FROM events WHERE active = %s """
                cur.execute(select, ('X',))
                record = cur.fetchone()
                if record is None:
                    players.sort(key=sort_by_mmr, reverse=True)
                    # обработка на случай одинакового ммр
                    unique_mmr = []
                    for player in players:
                        while player.mmr in unique_mmr:
                            player.mmr = float(player.mmr) + 0.1
                        unique_mmr.append(player.mmr)
                    team_one_mmr, team_two_mmr = min_diff_sets(
                        [float(player.mmr) for index, player in enumerate(players[:-2])])
                    team_one_mmr += (float(players[-1].mmr),)
                    team_two_mmr += (float(players[-2].mmr),)
                    team_one = [player for player in players if float(player.mmr) in team_one_mmr]
                    team_two = [player for player in players if float(player.mmr) in team_two_mmr]
                    print(team_one)
                    now = str(datetime.now(pytz.timezone('Europe/Moscow')))[:19]
                    insert = """INSERT INTO events(TIME, ADMIN, ACTIVE, 
                    blue01, blue02, blue03, blue04, blue05, 
                    red01, red02, red03, red04, red05)
                    VALUES (%s, %s, %s, 
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s )"""
                    cur.execute(insert, (now, ctx.message.author.name, 'X',
                                         team_one[0].btag, team_one[1].btag, team_one[2].btag, team_one[3].btag,
                                         team_one[4].btag,
                                         team_two[0].btag, team_two[1].btag, team_two[2].btag, team_two[3].btag,
                                         team_two[4].btag))
                    con.commit()
                    con.close()
                    team_one_discord = ' '.join([get_player_data(player) for player in team_one])
                    team_two_discord = ' '.join([get_player_data(player) for player in team_two])
                    await ctx.send(f"**Синяя команда:** \n{team_one_discord}")
                    await ctx.send(f"**Красная команда:** \n{team_two_discord}")  # mean(team_blue):.2f
                else:
                    await ctx.send(f"Для создания нового матча завершите предыдущий")

    @event.command(name="winner")
    @check.is_admin()
    async def event_winner(self, ctx, winner, delta):
        if winner == 'blue' or winner == 'red':
            bonus = 3
            delta = int(delta) * bonus
            sql.sql_init()
            con = sql.get_connect()
            cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            select = """SELECT * FROM events WHERE active = 'X'"""
            cur.execute(select)
            record = cur.fetchone()
            if record is not None:
                if winner == 'blue':
                    win_team = [record.blue01, record.blue02, record.blue03, record.blue04, record.blue05]
                    lose_team = [record.red01, record.red02, record.red03, record.red04, record.red05]
                elif winner == 'red':
                    lose_team = [record.blue01, record.blue02, record.blue03, record.blue04, record.blue05]
                    win_team = [record.red01, record.red02, record.red03, record.red04, record.red05]
                update = """UPDATE events SET winner = %s, delta_mmr = %s, active = %s WHERE active = %s"""
                cur.execute(update, (winner, delta, ' ', 'X'))
                await ctx.send(f"Матч успешно закрыт")
                for player in win_team:
                    await self.profile_delta(ctx, player.replace(' ', ''), delta)
                await ctx.send(f"Очки за победу начислены")
                for player in lose_team:
                    await self.profile_delta(ctx, player.replace(' ', ''), delta, '-')
                await ctx.send(f"Очки за поражение начислены")
            else:
                await ctx.send(f"Открытых матчей не найдено")
            con.commit()
            con.close()
        else:
            await ctx.send(f"Укажите победителя *red* или *blue*")

    @event.command(name="remove")
    @check.is_admin()
    async def event_remove(self, ctx):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM events WHERE active = 'X'"""
        cur.execute(select)
        record = cur.fetchone()
        if record is not None:
            delete = """DELETE FROM events WHERE active = 'X'"""
            cur.execute(delete)
            con.commit()
            con.close()
            await ctx.send(f"Активный матч был отменен, можно пересоздать команды")

    @commands.group(name="profile")
    async def profile(self, ctx):
        """
        - Связь батлтега и дискорд профиля
        """
        if ctx.invoked_subcommand is None:
            await self.profile_info(ctx, ctx.subcommand_passed)
            #await ctx.send('Для добавления игрока используйте команду #profile add батлтег дискорд\n '
            #               'Пример: *#profile add player#1234 @player*')

    @profile.command(name="test")
    @check.is_admin()
    async def profile_test(self, ctx, *, avamember: Member = None):
        # userAvatarUrl = avamember.avatar_url
        await ctx.send('Тест прав пройден')

    @profile.command(name="add")
    async def profile_add(self, ctx, btag, discord_user):
        print("profile_add")
        member = get_discord_id(discord_user)
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor()
        select = """SELECT * FROM heroesprofile WHERE btag = %s"""
        cur.execute(select, (btag,))
        record = cur.fetchone()
        print(record)
        if record is None:
            data = get_heroesprofile_data(btag, member)
            print(data)
            if data is not None:
                insert = """INSERT INTO heroesprofile(BTAG, RANK, DIVISION, WINRATE, MMR, DISCORD) 
                            VALUES(%s, %s, %s, %s, %s, %s )"""
                cur.execute(insert, (data.btag, data.league, data.division, data.winrate, data.mmr, data.discord))
                con.commit()
                con.close()
                await ctx.send(f"Профиль игрока {btag} добавлен в базу")
            else:
                await ctx.send(f'Профиль игрока {btag} не найден')

    @profile.command(name="remove")
    @check.is_admin()
    async def profile_remove(self, ctx, user_or_btag):
        member = get_discord_id(user_or_btag)
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        delete = """DELETE FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(delete, (member, user_or_btag,))
        con.commit()
        con.close()
        await ctx.send(f"Профиль {user_or_btag} удален из базы")

    @profile.command(name="fix")
    @check.is_admin()
    async def profile_fix(self, ctx, user_or_btag, league, division, mmr):
        member = get_discord_id(user_or_btag)
        print(member)
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(select, (member, user_or_btag,))
        record = cur.fetchone()
        if record is not None:
            player = get_player(record)
            print(player)
            update = """UPDATE heroesprofile SET RANK = %s, DIVISION = %s, MMR = %s WHERE btag=%s"""
            cur.execute(update, (league, division, mmr, player.btag))
            con.commit()
            con.close()
            await ctx.send(f"Профиль игрока {player.btag} обновлен")
        else:
            await ctx.send(f"Профиль {user_or_btag} не найден в базе. Добавьте его командой #profile add")

    @profile.command(name="delta")
    async def profile_delta(self, ctx, btag, delta, plus='+'):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile WHERE btag = %s"""
        cur.execute(select, (btag,))
        record = cur.fetchone()
        if record is not None:
            if plus == '+':
                mmr_new = int(record.mmr) + int(delta)
                winrate_new = record.win + 1
                update = """UPDATE heroesprofile SET win = %s, mmr = %s WHERE btag = %s"""
            else:
                mmr_new = int(record.mmr) - int(delta)
                winrate_new = record.lose + 1
                update = """UPDATE heroesprofile SET lose = %s, mmr = %s WHERE btag = %s"""
            cur.execute(update, (winrate_new, mmr_new, btag))
            con.commit()
            con.close()

    @profile.command(name="update")
    @check.is_admin()
    async def profile_update(self, ctx, *args):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        for user in args:
            member = get_discord_id(user)
            select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
            cur.execute(select, (member, user,))
            record = cur.fetchone()
            if record is not None:
                player = get_player(record)
                print(player.discord)
                try:
                    data = get_heroesprofile_data(player.btag, player.discord)
                    update = """UPDATE heroesprofile SET RANK = %s, WINRATE = %s, MMR = %s, WIN = %s, LOSE = %s WHERE btag=%s"""
                    cur.execute(update, (data.league, data.winrate, data.mmr, player.win, player.lose, data.btag,))
                    await ctx.send(f"Профиль игрока {player.btag} обновлен")
                except:
                    await ctx.send(f'Сайт не вернул данные, повторите запрос чуть позднее или напишите *fenrir#5455*')
            else:
                await ctx.send(f"Профиль {user} не найден в базе. Добавьте его командой #profile add")
        con.commit()
        con.close()

    @profile.command(name="info")
    async def profile_info(self, ctx, user_or_btag):
        sql.sql_init()
        con = sql.get_connect()
        member = get_discord_id(user_or_btag)
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(select, (member, user_or_btag,))
        record = cur.fetchone()
        print(record)
        if record is not None:
            player = get_player(record)
            print(player)
            if player is not None:
                embed = get_profile_embed(player)
                try:  # на случай запроса с другого сервера
                    member = ctx.guild.get_member(int(player.discord))
                    user_avatar = avatar(ctx, member)
                    embed.set_thumbnail(
                        url=user_avatar
                    )
                except:
                    pass
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"Профиль {user_or_btag} не найден в базе. Добавьте его командой #profile add")
        con.close()

    @profile.command(name="btag")
    async def profile_btag(self, ctx, member_discord):
        sql.sql_init()
        con = sql.get_connect()
        member = get_discord_id(member_discord)
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile WHERE discord = %s"""
        cur.execute(select, (member,))
        record = cur.fetchone()
        if record is not None:
            player = get_player(record)
            await ctx.send(f"Батлтег {get_discord_mention(member_discord)}: *{player.btag}*")
        else:
            await ctx.send(profile_not_found(member_discord))
        con.close()

    @commands.group(name="search")
    async def search(self, ctx):
        '''

        :param ctx:
        :return:
        '''
        if ctx.invoked_subcommand is None:
            await Profile.search_team(self, ctx)

    @search.command(name="team")
    async def search_team(self, ctx, league=None):
        profile, con, cur = get_profile_by_discord(str(ctx.message.author.id))
        if profile is not None:
            if not profile.search:
                profile.search = True
                await ctx.send("Ваш профиль добавлен в ищущих группу\n"
                               "Для отключения наберите *!search off*")
                update = '''UPDATE heroesprofile SET search = %s WHERE discord = %s'''
                cur.execute(update, (profile.search, profile.discord))
            if league is None:
                league = profile.league
            select = '''SELECT * FROM heroesprofile WHERE rank = %s AND search = %s'''
            cur.execute(select, (league, profile.search))
            record = cur.fetchall()
            if (len(record) == 0) or \
                    (len(record) == 1 and record[0].discord == str(ctx.message.author.id)):
                await ctx.send(f"В данный момент нет игроков ранга {league} ищущих группу")
            else:
                await ctx.send(f"Игроки уровня {league}, которых сейчас можно позвать в пати:")
                message = ''
                for players in record:
                    player = get_player(players)
                    await Profile.profile_info(self, ctx, player.discord)
        else:
            await ctx.send("Чтобы воспользоваться поиском ваш профиль должен быть добавлен в базу\n"
                           "Используйте команду ```!profile add батлтаг#1234 @дискорд```")
        con.commit()
        con.close()

    @search.command(name="on")
    async def search_on(self, ctx):
        profile, con, cur = get_profile_by_discord(str(ctx.message.author.id))
        if profile is not None:
            profile.search = True
            update = '''UPDATE heroesprofile SET search = %s WHERE discord = %s'''
            cur.execute(update, (profile.search, profile.discord))
            await ctx.send("Вы добавлены в ищущих группу")
        else:
            await ctx.send("Ваш профиль не добавлен в базу\n"
                           "Используйте команду ```!profile add батлтаг#1234 @дискорд```")

    @search.command(name="off")
    async def search_off(self, ctx):
        profile, con, cur = get_profile_by_discord(str(ctx.message.author.id))
        if profile is not None:
            profile.search = False
            update = '''UPDATE heroesprofile SET search = %s WHERE discord = %s'''
            cur.execute(update, (profile.search, profile.discord))
            await ctx.send("Поиск игроков отключен")
        else:
            await ctx.send("Ваш профиль не добавлен в базу\n"
                           "Используйте команду ```!profile add батлтаг#1234 @дискорд```")

    @commands.group(name="fix")
    @check.is_owner()
    async def fix(self, ctx):
        """
        - Исправление ошибок в БД
        :param ctx:
        :return:
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Выберите что исправлять")

    @fix.command(name="divisions")
    @check.is_owner()
    async def fix_divisions(self, ctx):
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
                    update = """UPDATE heroesprofile SET rank = %s, division = %s WHERE btag=%s"""
                    cur.execute(update, (player.league, division, player.btag))
            await ctx.send("Записи были разделены на дивизионы")
        else:
            await ctx.send("Нет прав на выполнение команды")
        con.commit()
        con.close()

    @fix.command(name="mmr")
    @check.is_owner()
    async def fix_mmr(self, ctx):
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
            player.mmr = ''.join([i for i in player.mmr if i.isdigit()]).replace(' ', '')
            update = '''UPDATE heroesprofile SET mmr = %s WHERE btag=%s'''
            cur.execute(update, (player.mmr, player.btag))
        await ctx.send("В записях был исправлен mmr")
        con.commit()
        con.close()

    @fix.command(name="discord")
    @check.is_owner()
    async def fix_discord(self, ctx):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        select = """SELECT * FROM heroesprofile"""
        cur.execute(select)
        rec = cur.fetchall()
        for player_list in rec:
            discord = get_discord_id(player_list['discord'])
            update = '''UPDATE heroesprofile SET discord = %s WHERE btag=%s'''
            cur.execute(update, (discord, player_list['btag']))
        await ctx.send("В записях был исправлен id")
        con.commit()
        con.close()

    @profile.error
    @profile_add.error
    @profile_test.error
    async def profile_handler(self, ctx, error):
        print("Попали в обработку ошибок")
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Не хватает аргументов. Необходимо указать батлтег и дискорд профиль\n"
                           "Пример: *#profile add player#1234 @player*")
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('Недостаточно прав')
        if isinstance(error, exceptions.UserNotOwner):
            await ctx.send(error.message)
        if isinstance(error, exceptions.UserNotAdmin):
            await ctx.send(exceptions.UserNotAdmin.message)


def setup(bot):
    bot.add_cog(Profile(bot))
