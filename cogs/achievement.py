import os
import yaml
from discord import Member
from discord.ext import commands
from datetime import date
from helpers import profile_lib as pl
from helpers import sql, check

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

class Team(commands.Cog, name="Team"):
    """
    — Описание модуля Достижений
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="achievement")
    async def achievement(self, ctx):
        if ctx.invoked_subcommand is None:
            con, cur = pl.get_con_cur()
            guild_id = pl.get_guild_id(ctx)
            select = pl.selects.get("achievAll")
            cur.execute(select, (guild_id, ))
            records = cur.fetchall()
            achievements = ''
            for record in records:
                achievements += f'{record.name}, id = **{record.id}**\n'
            await ctx.send(achievements)


    @achievement.command(name="create")
    @check.is_admin()
    async def achievement_create(self, ctx, *name):
        con, cur = pl.get_con_cur()
        guild_id = pl.get_guild_id(ctx)
        achiev_name = ' '.join(name)
        insert = pl.inserts.get("Achievement")
        cur.execute(insert, (guild_id, achiev_name))
        record = cur.fetchone()
        pl.commit(con)
        await ctx.send(f'Добавлено достижение {achiev_name} (id: {record.id})')

    @achievement.command(name="assign")
    @check.is_admin()
    async def achievement_assign(self, ctx, member: Member, id):
        con, cur = pl.get_con_cur()
        guild_id = pl.get_guild_id(ctx)
        select = pl.selects.get("achievId")
        cur.execute(select, (id, ))
        record = cur.fetchone()
        print(record)
        today = date.today()
        insert = pl.inserts.get("UserAchiev")
        cur.execute(insert, (member.id, guild_id, id, today))
        pl.commit(con)
        await ctx.send(f"{member.mention} теперь **{record.name}**")

    @achievement.command(name="remove")
    @check.is_admin()
    async def achievement_remove(self, ctx, member: Member, id):
        con, cur = pl.get_con_cur()
        guild_id = pl.get_guild_id(ctx)
        select = pl.selects.get("achievId")
        cur.execute(select, (id,))
        record = cur.fetchone()
        achiev_name = record.name
        delete = pl.deletes.get("UserAchiev")
        cur.execute(delete, (member.id, guild_id, id))
        if cur.rowcount:
            pl.commit(con)
            await ctx.send(f"С игрока {member.mention} снято достижение **{achiev_name}**")
        else:
            await ctx.send(f"У игрока {member.mention} нет достижения **{achiev_name}**")

    @achievement.command(name="delete")
    @check.is_admin()
    async def achievement_delete(self, ctx, id: int):
        con, cur = pl.get_con_cur()
        guild_id = pl.get_guild_id(ctx)
        delete = pl.deletes.get("AchievId")
        cur.execute(delete, (id, guild_id))
        achiev_name = cur.fetchone()[0]
        if cur.rowcount:
            pl.commit(con)
            await ctx.send(f"Достижение **{achiev_name}** удалено")
        else:
            await ctx.send(f"Нет достижения с **id={id}**")


def setup(bot):
    bot.add_cog(Team(bot))