import os
import yaml
import psycopg2.extras
import exceptions
from discord.ext import commands
from helpers import sql, check
from psycopg2 import errorcodes
from discord import Embed, utils, Member
from helpers import profile_lib as pl

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class Points(commands.Cog, name="Points"):
    """
    — Использование баллов
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="points")
    async def points(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.profile_info(ctx, ctx.subcommand_passed)

    @points.command(name="top")
    async def points_top(self, ctx, count=10):
        con, cur = pl.get_con_cur()
        select = pl.selects.get("usPoints")
        cur.execute(select, (count, ))
        records = cur.fetchall()
        embed = Embed(
            title=f"Таблица лидеров",
            color=config["info"]
        )
        value = ""
        for i, record in enumerate(records):
            value += f"{i+1}. {pl.get_discord_mention(record.id)} - {record.points}\n"
        embed.add_field(
            name=f"Топ {count} игроков",
            value=value
        )
        await ctx.send(embed=embed)

    @points.command(name="pay"):
    async def points_pay(self, ctx, user: Member, count=0):
        con, cur = pl.get_con_cur()
        id = pl.get_user_id(user.id)
        guild_id =pl.get_guild_id(ctx)
        select = pl.selects.get("usIdGuild")
        cur.execute(select, (id, guild_id))
        record = cur.fetchone()
        stats = pl.get_stats(record)
        if stats.points < count:
            await ctx.send("Недостаточно баллов")
        else:
            stats.points -= count
            update = pl.updates.get("StatsPoints")
            cur.execute(update, (stats.points, stats.id, stats.guild_id))
            pl.commit(con)
            await ctx.send("Баллы успешно сняты")



def setup(bot):
    bot.add_cog(Points(bot))