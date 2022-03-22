""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

from discord import Member
from discord.ext import commands
from datetime import date
from utils.classes import Const
from utils import exceptions, library, check
from utils.classes.Const import config


class Team(commands.Cog, name="Team"):
    """
    — Описание модуля Достижений
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="achievement")
    async def achievement(self, ctx):
        if ctx.invoked_subcommand is None:
            con, cur = library.get.con_cur()
            guild_id = library.get.guild_id(ctx)
            select = Const.selects.AchievGuild
            cur.execute(select, (guild_id,))
            records = cur.fetchall()
            con.close()
            achievements = ''
            for record in records:
                achievements += f'{record.name}, id = **{record.id}**\n'
            await ctx.send(achievements)

    @achievement.command(name="create")
    @check.is_admin()
    async def achievement_create(self, ctx, *name):
        con, cur = library.get.con_cur()
        guild_id = library.get.guild_id(ctx)
        achiev_name = ' '.join(name)
        insert = Const.inserts.Achievement
        cur.execute(insert, (guild_id, achiev_name))
        record = cur.fetchone()
        library.commit(con)
        await ctx.send(f'Добавлено достижение {achiev_name} (id: {record.id})')

    @achievement.command(name="assign")
    @check.is_admin()
    async def achievement_assign(self, ctx, member: Member, id):
        con, cur = library.get.con_cur()
        guild_id = library.get.guild_id(ctx)
        select = Const.selects.AchievId
        cur.execute(select, (id,))
        record = cur.fetchone()
        print(record)
        today = date.today()
        insert = Const.inserts.UserAchiev
        cur.execute(insert, (member.id, guild_id, id, today))
        library.commit(con)
        await ctx.message.delete()
        await ctx.send(f"{member.mention} теперь **{record.name}**")

    @achievement.command(name="remove")
    @check.is_admin()
    async def achievement_remove(self, ctx, member: Member, id):
        con, cur = library.get.con_cur()
        guild_id = library.get.guild_id(ctx)
        select = Const.selects.AchievId
        cur.execute(select, (id,))
        record = cur.fetchone()
        achiev_name = record.name
        delete = Const.deletes.UserAchiev
        cur.execute(delete, (member.id, guild_id, id))
        if cur.rowcount:
            library.commit(con)
            await ctx.send(f"С игрока {member.mention} снято достижение **{achiev_name}**")
        else:
            con.close()
            await ctx.send(f"У игрока {member.mention} нет достижения **{achiev_name}**")

    @achievement.command(name="delete")
    @check.is_admin()
    async def achievement_delete(self, ctx, id: int):
        con, cur = library.get.con_cur()
        guild_id = library.get.guild_id(ctx)
        delete = Const.deletes.AchievId
        cur.execute(delete, (id, guild_id))
        achiev_name = cur.fetchone()[0]
        if cur.rowcount:
            library.commit(con)
            await ctx.send(f"Достижение **{achiev_name}** удалено")
        else:
            con.close()
            await ctx.send(f"Нет достижения с **id={id}**")


def setup(bot):
    bot.add_cog(Team(bot))
