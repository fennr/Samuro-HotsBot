""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import psycopg2.extras
from psycopg2 import errorcodes, errors
import discord
from discord.ext import commands

import utils.library.embeds
from utils.classes import Const
from utils import exceptions, library, check, classes

UniqueViolation = errors.lookup(psycopg2.errorcodes.UNIQUE_VIOLATION)


class Profile(commands.Cog, name="Profile"):
    """
    — Связь дискорд профиля с батлнет профилем
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="login")
    async def login(self, ctx, battletag: str):
        author_id = library.get.author_id(ctx)
        con, cur = library.get.con_cur()
        select = Const.selects.PlayersId
        cur.execute(select, (author_id, ))
        record = cur.fetchone()
        if record is None:
            player = library.get_heroesprofile_data(btag=battletag,
                                                    user_id=author_id,
                                                    guild_id=library.get.guild_id(ctx))
            if isinstance(player, classes.Player):
                con, cur = library.get.con_cur()
                insert = Const.inserts.Player
                cur.execute(insert, (player.btag, player.id, player.guild_id,
                                     player.mmr, player.league, player.division))
                library.commit(con)
                try:
                    await library.add_role(ctx, player, player.league)
                    await ctx.send(f"Посмотреть свой профиль можно командой *!profile*. Добро пожаловать.")
                except Exception:
                    print(Exception)
            else:
                await ctx.send(library.profile_not_found(battletag))
        else:
            player = library.get.player(record)
            print(player)
            try:
                await library.add_role(ctx, player, player.league)
            except Exception:
                print(Exception)

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
        con, cur = library.get.con_cur()
        user_id = library.get.user_id(user)
        select = Const.selects.PlayersIdOrBtag
        cur.execute(select, (user_id, user,))
        player = library.get.player(cur.fetchone())
        print(player)
        print(type(player))
        con.close()

    @profile.command(name="add")
    async def profile_add(self, ctx, btag: str, discord_user: discord.Member):
        """
        — Добавить аккаунт в базу
        """
        print(discord_user)
        player = library.get_heroesprofile_data(btag=btag,
                                                user_id=library.get.user_id(discord_user),
                                                guild_id=library.get.guild_id(ctx))
        if isinstance(player, classes.Player):
            con, cur = library.get.con_cur()
            insert = Const.inserts.Player
            cur.execute(insert, (player.btag, player.id, player.guild_id,
                                 player.mmr, player.league, player.division))
            library.commit(con)
            await ctx.send(f"Профиль игрока {btag} добавлен в базу")
            try:
                await library.add_role(ctx, player, player.league)
                await ctx.send(f"Посмотреть свой профиль можно командой *!profile*. Добро пожаловать.")
            except Exception:
                print(Exception)
        else:
            await ctx.send(library.profile_not_found(btag))

    @profile.command(name="remove")
    @check.is_owner()
    async def profile_remove(self, ctx, user_or_btag):
        user_id = library.get.user_id(user_or_btag)
        con, cur = library.get.con_cur()
        delete = Const.deletes.PlayerIdOrBtag
        cur.execute(delete, (user_id, user_or_btag,))
        library.commit(con)
        await ctx.send(f"Профиль {user_or_btag} удален из базы")

    # в фиксе оставить только ММР после фунции, которая пересчитывает лигу
    @profile.command(name="fix")
    @check.is_admin()
    async def profile_fix(self, ctx, user_or_btag, mmr):
        """
        — Исправить ММР игрока (admin only)
        """
        user_id = library.get.user_id(user_or_btag)
        con, cur = library.get.con_cur()
        select = Const.selects.PlayersIdOrBtag
        cur.execute(select, (user_id, user_or_btag,))
        player = library.get.player(cur.fetchone())
        if player is not None:
            player.mmr = mmr
            old_league = player.league
            player.league, player.division = library.get.league_division_by_mmr(int(mmr))
            if (old_league != player.league):
                try:
                    await library.remove_role(ctx, player, old_league)
                    await library.add_role(ctx, player, player.league)
                except Exception:
                    print(f"Не созданы роли {old_league}, {player.league}")
            update = Const.updates.PlayerMMR
            cur.execute(update, (player.mmr, player.league, player.division, player.id))
            con.commit()
            con.close()
            await ctx.send(f"Профиль игрока {player.btag} обновлен")
        else:
            await ctx.send(library.profile_not_found(user_or_btag))

    @profile.command(name="update")
    @check.is_admin()
    async def profile_update(self, ctx, *args):
        con, cur = library.get.con_cur()
        for user in args:
            user_id = library.get.user_id(user)
            select = Const.selects.PlayersIdOrBtag
            cur.execute(select, (user_id, user,))
            player = library.get.player(cur.fetchone())
            if player is not None:
                player_new = library.get_heroesprofile_data(player.btag, player.id, ctx.guild.id)
                player_new.league, player_new.division = library.get.league_division_by_mmr(player_new.mmr)
                update = Const.updates.PlayerMMR
                cur.execute(update, (player_new.mmr, player_new.league, player_new.division,
                                     player_new.id))
                await ctx.send(f"Профиль игрока {player.btag} обновлен")
            else:
                await ctx.send(library.profile_not_found(user))
        library.commit(con)

    @profile.command(name="info")
    async def profile_info(self, ctx, user_or_btag):
        """
        — Получить информацию о профиле
        """
        con, cur = library.get.con_cur()
        user_id = library.get.user_id(user_or_btag)
        guild_id = library.get.guild_id(ctx)
        select = Const.selects.PlayersIdOrBtag
        cur.execute(select, (user_id, user_or_btag,))
        player = library.get.player(cur.fetchone())
        if player is not None:
            try:
                await library.add_role(ctx, player, player.league, message=False)
            except:
                print(f"Нет роли {player.league}")
            embed = utils.library.embeds.profile(ctx, player)
            select = Const.selects.USIdGuild
            cur.execute(select, (player.id, guild_id))
            stats = library.get.stats(cur.fetchone())
            if stats is not None:
                embed = utils.library.embeds.stats(embed, stats)
            embed = utils.library.embeds.votes(embed, player)
            if player.team is not None:
                embed = utils.library.embeds.user_team(embed, player.team)
            embed = utils.library.embeds.achievements(embed, player)
            guild = [guild for guild in self.bot.guilds if guild.id == player.guild_id][0]
            member = guild.get_member(int(player.id))
            user_avatar = library.avatar(ctx, member)
            embed.set_thumbnail(
                url=user_avatar
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(library.profile_not_found(user_or_btag))
        con.close()

    @profile.command(name="btag")
    async def profile_btag(self, ctx, member_discord):
        """
        — Посмотреть батлтаг профиля
        """
        con, cur = library.get.con_cur()
        user_id = library.get.user_id(member_discord)
        select = Const.selects.PlayersId
        cur.execute(select, (user_id,))
        player = library.get.player(cur.fetchone())
        if player is not None:
            await ctx.send(f"Батлтег {member_discord}: *{player.btag}*")
        else:
            await ctx.send(library.profile_not_found(member_discord))
        con.close()

    @profile.error
    @profile_add.error
    @profile_test.error
    async def profile_handler(self, ctx, error):
        # print("Попали в обработку ошибок profile")
        error = getattr(error, 'original', error)  # получаем пользовательские ошибки
        print(error)
        # print(type(error))
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Не хватает аргументов. Необходимо указать батлтег и дискорд профиль\n"
                           "Пример: */profile_add player#1234 @player*")
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('Недостаточно прав')
        if isinstance(error, exceptions.UserNotOwner):
            await ctx.send(error.message)
        if isinstance(error, exceptions.UserNotAdmin):
            await ctx.send(exceptions.UserNotAdmin.message)
        if isinstance(error, exceptions.LeagueNotFound):
            await ctx.send("Не найдены игры в шторм лиге")
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Неверно введены аргументы")
        if isinstance(error, UniqueViolation):
            await ctx.send("Обнаружен дубликат записи. Профили дискорда и батлтаги должны быть уникальны")


def setup(bot):
    bot.add_cog(Profile(bot))
