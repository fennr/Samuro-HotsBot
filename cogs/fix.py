""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import psycopg2.extras
from discord.ext import commands
import discord
from utils.library import files, profile as pl
from utils import check, sql
from utils.classes.Player import Player
from utils.classes import Const
from utils import exceptions, sql, library

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

    @fix.command(name="role")
    @check.is_owner()
    async def fix_role(self, ctx, role_id: int):
        role = discord.utils.get(ctx.message.guild.roles, id=role_id)
        if role:
            await role.edit(mentionable=True)
            await ctx.send(f"Добавлена возможность тегать роль {role.mention}")
        else:
            await ctx.send(f"Не найдена роль id={role}")

    @fix.command(name="command_role")
    @check.is_owner()
    async def fix_command_role(self, ctx, role: discord.Role):
        try:
            command_role_id = 796717939239813141  # Роли
            command_role = discord.utils.get(ctx.message.guild.roles, id=command_role_id)
            await role.edit(position=command_role.position)
            print(f"Роль добавлена в раздел с ролями")
        except:
            print(f"Ошибка перемещения роли")

    @fix.command(name="base_role")
    @check.is_owner()
    async def fix_base_role(self, ctx, role: discord.Role):
        try:
            command_role_id = 796717939239813141  # Роли
            command_role = discord.utils.get(ctx.message.guild.roles, id=command_role_id)
            await role.edit(position=command_role.position-1)
            print(f"Роль добавлена в раздел с ролями")
        except:
            print(f"Ошибка перемещения роли")

    @fix.command(name="role_color")
    @check.is_owner()
    async def role_up_color(self, ctx, role: discord.Role, color: discord.Colour):
        pos = len(ctx.guild.roles)
        while True:
            try:
                await role.edit(position=pos)
                print(f'Роль поднята до позиции {pos}')
                break
            except:
                pos -= 1
                if pos < 1:
                    break
        await role.edit(color=color)

    @fix.command(name="new_role")
    @check.is_owner()
    async def fix_new_role(self, ctx, role_name, color=discord.Colour.red()):
        role = await ctx.guild.create_role(name=role_name, color=color, mentionable=True)
        await ctx.send(f"Создана роль {role.mention}")

    @fix.command(name="points")
    @check.is_owner()
    async def fex_points(self, ctx):
        con, cur = library.get.con_cur()
        guild_id = library.get.guild_id(ctx)
        select = Const.selects.US
        cur.execute(select)
        rec = cur.fetchall()
        for record in rec:
            stats = library.get.stats(record)
            stats.points = stats.win * 3 + stats.lose * 1
            update = Const.updates.USPoints
            cur.execute(update, (stats.points, stats.id, stats.guild_id))
        library.commit(con)
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
                if player.league == 'Master' or player.league == 'Grandmaster':
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

    @fix.command(name="league")
    @check.is_owner()
    async def fix_league(self, ctx):
        sql.sql_init()
        con, cur = pl.get_con_cur()
        select = pl.selects.get('PlayersAll')
        cur.execute(select)
        rec = cur.fetchall()
        for record in rec:
            player = pl.get_player(record)
            player.league, player.division = pl.get_league_division_by_mmr(player.mmr)
            update = pl.updates.get('PlayerMMR')
            cur.execute(update, (player.league, player.division, player.mmr,
                                 player.id))
            if (str(record.league) != str(player.league)) or (str(record.division) != str(player.division)):
                print(f"Лига игрока {player.btag} исправлена: "
                      f"{record.league} {record.division} -> {player.league} {player.division}")
        pl.commit(con)
        await ctx.send("Лиги игроков были исправлены")

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
                            mmr=player_list['mmr'])
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
