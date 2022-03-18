import os
import yaml
import psycopg2.extras
from discord.ext import commands
from psycopg2 import errorcodes, errors
from utils import check, exceptions, sql
from utils.library import profile as pl

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

UniqueViolation = errors.lookup(psycopg2.errorcodes.UNIQUE_VIOLATION)


class Profile(commands.Cog, name="Profile"):
    """
    — Связь дискорд профиля с батлнет профилем
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="profile")
    async def profile(self, ctx):
        """
        — Посмотреть свой профиль
        """
        if ctx.invoked_subcommand is None:
            try:
                await self.profile_info(ctx, ctx.subcommand_passed)
            except:
                await self.profile_info(ctx, str(ctx.message.author.mention))
            # await ctx.send('Для добавления игрока используйте команду #profile add батлтег дискорд\n '
            #               'Пример: *#profile add player#1234 @player*')

    @profile.command(name="test")
    @check.is_admin()
    async def profile_test(self, ctx, user):
        con, cur = pl.get_con_cur()
        user_id = pl.get_user_id(user)
        select = pl.selects.get('PlayersIdOrBtag')
        cur.execute(select, (user_id, user,))
        player = pl.get_player(cur.fetchone())
        print(player)
        print(type(player))
        con.close()

    @profile.command(name="add")
    async def profile_add(self, ctx, btag, discord_user):
        """
        — Добавить аккаунт в базу
        """
        player = pl.get_heroesprofile_data(btag=btag,
                                           user_id=pl.get_user_id(discord_user),
                                           guild_id=pl.get_guild_id(ctx))
        if isinstance(player, utils.hots.Player.Player):
            con, cur = pl.get_con_cur()
            insert = pl.inserts.get('Player')
            cur.execute(insert, (player.btag, player.id, player.guild_id,
                                 player.mmr, player.league, player.division))
            pl.commit(con)
            await ctx.send(f"Профиль игрока {btag} добавлен в базу")
        else:
             await ctx.send(pl.profile_not_found(btag))

    @profile.command(name="remove")
    @check.is_owner()
    async def profile_remove(self, ctx, user_or_btag):
        user_id = pl.get_user_id(user_or_btag)
        con, cur = pl.get_con_cur()
        delete = pl.deletes.get('PlayerIdOrBtag')
        cur.execute(delete, (user_id, user_or_btag,))
        pl.commit(con)
        await ctx.send(f"Профиль {user_or_btag} удален из базы")

    # в фиксе оставить только ММР после фунции, которая пересчитывает лигу
    @profile.command(name="fix")
    @check.is_admin()
    async def profile_fix(self, ctx, user_or_btag, mmr):
        """
        — Исправить ММР игрока (admin only)
        """
        user_id = pl.get_user_id(user_or_btag)
        con, cur = pl.get_con_cur()
        select = pl.selects.get('PlayersIdOrBtag')
        cur.execute(select, (user_id, user_or_btag,))
        player = pl.get_player(cur.fetchone())
        if player is not None:
            player.mmr = mmr
            player.league, player.division = pl.get_league_division_by_mmr(int(mmr))
            update = pl.updates.get('PlayerMMR')
            cur.execute(update, (player.league, player.division, player.mmr, player.id))
            con.commit()
            con.close()
            await ctx.send(f"Профиль игрока {player.btag} обновлен")
        else:
            await ctx.send(pl.profile_not_found(user_or_btag))

    #удалить данную команду, сделать просто функцию с дельтой куда передается Player,
    # внутри дельты проверку на изменение лиги и изменение ее тоже
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
                mmr_new = record.mmr + int(delta)
                winrate_new = record.win + 1
                update = """UPDATE heroesprofile SET win = %s, mmr = %s WHERE btag = %s"""
            else:
                mmr_new = record.mmr - int(delta)
                winrate_new = record.lose + 1
                update = """UPDATE heroesprofile SET lose = %s, mmr = %s WHERE btag = %s"""
            cur.execute(update, (winrate_new, mmr_new, btag))
            con.commit()
            con.close()

    @profile.command(name="update")
    @check.is_admin()
    async def profile_update(self, ctx, *args):
        con, cur = pl.get_con_cur()
        for user in args:
            user_id = pl.get_user_id(user)
            select = pl.selects.get('PlayersIdOrBtag')
            cur.execute(select, (user_id, user, ))
            player = pl.get_player(cur.fetchone())
            if player is not None:
                player_new = pl.get_heroesprofile_data(player.btag, player.id, ctx.guild.id)
                update = '''UPDATE "Players" SET MMR = %s WHERE id=%s'''
                cur.execute(update, (player_new.mmr, player_new.id))
                await ctx.send(f"Профиль игрока {player.btag} обновлен")
            else:
                await ctx.send(pl.profile_not_found(user))
        pl.commit(con)

    @profile.command(name="info")
    async def profile_info(self, ctx, user_or_btag):
        """
        — Получить информацию о профиле
        """
        con, cur = pl.get_con_cur()
        user_id = pl.get_user_id(user_or_btag)
        guild_id = pl.get_guild_id(ctx)
        select = pl.selects.get('PlayersIdOrBtag')
        cur.execute(select, (user_id, user_or_btag,))
        player = pl.get_player(cur.fetchone())
        if player is not None:
            embed = pl.get_profile_embed(ctx, player)
            select = pl.selects.get('usIdGuild')
            cur.execute(select, (player.id, guild_id))
            stats = pl.get_stats(cur.fetchone())
            #print(stats)
            if stats is not None:
                embed = pl.get_stats_embed(embed, stats)
            if player.team is not None:
                embed = pl.get_user_team_embed(embed, player.team)
            embed = pl.get_achievements_embed(embed, player)
            guild = [guild for guild in self.bot.guilds if guild.id == player.guild_id][0]
            member = guild.get_member(int(player.id))
            user_avatar = pl.avatar(ctx, member)
            embed.set_thumbnail(
                url=user_avatar
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(pl.profile_not_found(user_or_btag))
        con.close()

    @profile.command(name="btag")
    async def profile_btag(self, ctx, member_discord):
        """
        — Посмотреть батлтаг профиля
        """
        con, cur = pl.get_con_cur()
        user_id = pl.get_user_id(member_discord)
        select = pl.selects.get('PlayersId')
        cur.execute(select, (user_id,))
        player = pl.get_player(cur.fetchone())
        if player is not None:
            await ctx.send(f"Батлтег {member_discord}: *{player.btag}*")
        else:
            await ctx.send(pl.profile_not_found(member_discord))
        con.close()

    @profile.error
    @profile_add.error
    @profile_test.error
    async def profile_handler(self, ctx, error):
        #print("Попали в обработку ошибок profile")
        error = getattr(error, 'original', error)  # получаем пользовательские ошибки
        print(error)
        #print(type(error))
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Не хватает аргументов. Необходимо указать батлтег и дискорд профиль\n"
                           "Пример: *#profile add player#1234 @player*")
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('Недостаточно прав')
        if isinstance(error, exceptions.UserNotOwner):
            await ctx.send(error.message)
        if isinstance(error, exceptions.UserNotAdmin):
            await ctx.send(exceptions.UserNotAdmin.message)
        if isinstance(error, exceptions.LeagueNotFound):
            await ctx.send("Не найдены игры в шторм лиге")
        if isinstance(error, UniqueViolation):
            await ctx.send("Обнаружен дубликат записи. Профили дискорда и батлтаги должны быть уникальны")


def setup(bot):
    bot.add_cog(Profile(bot))
