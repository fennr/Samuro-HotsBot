import os
import yaml
import psycopg2.extras
from discord.ext import commands
from helpers import sql, check
from hots.Player import Player
from helpers import profile_lib as pl

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class Fix(commands.Cog, name="Fix"):
    def __init__(self, bot):
        self.bot = bot

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

    @fix.command(name="points")
    @check.is_owner()
    async def fex_points(self, ctx):
        con, cur = pl.get_con_cur()
        guild_id = pl.get_guild_id(ctx)
        select = pl.selects.get("usAll")
        cur.execute(select)
        rec = cur.fetchall()
        for record in rec:
            stats = pl.get_stats(record)
            stats.points = stats.win * 3 + stats.lose * 1
            update = pl.updates.get("StatsPoints")
            cur.execute(update, (stats.points, stats.id, stats.guild_id))
        pl.commit(con)
        await ctx.send("Очки за все игры были пересчитаны")

    @fix.command(name="new_table")
    @check.is_owner()
    async def fix_new_table(self, ctx):
        con, cur = pl.get_con_cur()
        select = pl.selects.get('hpAll')
        cur.execute(select)
        rec = cur.fetchall()
        for record in rec:
            player = pl.get_player(record)
            player.league, player.division = pl.get_league_division_by_mmr(player.mmr)
            insert = '''INSERT INTO "Players"(btag, id, guild_id, mmr, league, division) 
                        VALUES (%s, %s, %s, %s, %s, %s)'''
            cur.execute(insert, (player.btag, player.id, player.guild_id,
                                 player.mmr, player.league, player.division))
        await ctx.send("Записи были перенесены в новую таблицу")
        pl.commit(con)

    @fix.command(name="userstats")
    @check.is_owner()
    async def fix_userstats(self, ctx):
        guild_id = pl.get_guild_id(ctx)
        con, cur = pl.get_con_cur()
        select = pl.selects.get('hpAll')
        cur.execute(select)
        rec = cur.fetchall()
        for record in rec:
            insert = '''INSERT INTO "UserStats"(id, guild_id, win, lose, points, btag) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id, guild_id) 
                        DO UPDATE SET btag = %s, win = %s, lose = %s'''
            cur.execute(insert, (record.id, record.guild_id,
                                 record.win, record.lose, 0, record.btag,
                                 record.btag, record.win, record.lose))
        await ctx.send("Данные о победах перенесены")
        pl.commit(con)

    @fix.command(name="guild_id")
    @check.is_owner()
    async def fix_guild_id(self, ctx):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        select = """SELECT * FROM heroesprofile"""
        cur.execute(select)
        rec = cur.fetchall()
        for player_list in rec:
            update = '''UPDATE heroesprofile SET guild_id = %s WHERE btag=%s'''
            cur.execute(update, (ctx.guild.id, player_list.btag))
        await ctx.send("В записях был исправлен guild_id")
        con.commit()
        con.close()

    @fix.command(name="divisions")
    @check.is_owner()
    async def fix_divisions(self, ctx):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        select = """SELECT * FROM heroesprofile"""
        cur.execute(select)
        rec = cur.fetchall()
        for player_list in rec:
            player = Player(btag=player_list['btag'], league=player_list['league'], division='',
                            id=player_list['id'],
                            mmr=player_list['mmr'], winrate=player_list['winrate'])
            if player.league[-1].isdigit():
                if player.league == 'Master':
                    division = 0
                else:
                    division = player.league[-1]
                    player.league = player.league[:-1]
                print(f"{player.league} {division}")
                update = """UPDATE heroesprofile SET league = %s, division = %s WHERE btag=%s"""
                cur.execute(update, (player.league, division, player.btag))
        await ctx.send("Записи были разделены на дивизионы")
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
            player = Player(btag=player_list['btag'], league=player_list['league'], division='',
                            id=player_list['id'],
                            mmr=player_list['mmr'], winrate=player_list['winrate'])
            # player.mmr = ''.join([i for i in player.mmr if i.isdigit()]).replace(' ', '')
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
            id = pl.get_discord_id(player_list['id'])
            update = '''UPDATE heroesprofile SET id = %s WHERE btag=%s'''
            cur.execute(update, (id, player_list['btag']))
        await ctx.send("В записях был исправлен id")
        con.commit()
        con.close()


def setup(bot):
    bot.add_cog(Fix(bot))
