import os
import yaml
import psycopg2.extras
import exceptions
from discord.ext import commands
from helpers import sql, check
from psycopg2 import errorcodes
from helpers import profile_lib as pl

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

class Team(commands.Cog, name="team"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="team")
    async def team(self, ctx):
        """
        - Команды для группы
        """
        if ctx.invoked_subcommand is None:
            pass

    @team.command(name="create")
    async def team_create(self, ctx, leader, team_name):
        con, cur = pl.get_con_cur()
        print(leader)
        player = pl.get_profile_by_id_or_btag(leader)
        if player is not None:
            insert = pl.inserts.get('Team')
            cur.execute(insert, (team_name, player.id))
            team_id = cur.fetchone()[0]
            update = pl.updates.get('PlayerTeam')
            cur.execute(update, (team_id, player.id))
            pl.commit(con)
            await ctx.send(f"Команда {team_name} создана")
        else:
            print("Для использования команды добавьте Ваш профиль в базу")

    @team.command(name="add")
    async def team_add(self, ctx, user):
        con, cur = pl.get_con_cur()
        user_id = pl.get_author_id(ctx)
        select = pl.selects.get('teamLid')
        cur.execute(select, (user_id, ))
        team = pl.get_team(cur.fetchone())
        if team is not None:
            player = pl.get_profile_by_id_or_btag(user)
            if player.team is None:
                updateP = pl.updates.get('PlayerTeam')
                print(team.id)
                print(player.id)
                cur.execute(updateP, (team.id, player.id, ))
                updateT = pl.updates.get('TeamMembers')
                cur.execute(updateT, (team.members+1, team.id, ))
                pl.commit(con)
                await ctx.send(f"Игрок <@{user_id}> добавлен в команду {team.name}.\n"
                               f"Всего игроков в команде - {team.members}")
        else:
            await ctx.send("У вас нет прав на добавление участников в команду")

    @team.command(name="remove")
    async def team_remove(self, ctx, user):
        con, cur = pl.get_con_cur()
        user_id = pl.get_author_id(ctx)
        select = pl.selects.get('teamLid')
        cur.execute(select, (user_id, ))
        team = pl.get_team(cur.fetchone())
        print(team)
        if team is not None:
            player = pl.get_profile_by_id_or_btag(user)
            print(player)
            if player.team is not None:
                updateP = pl.updates.get('PlayerTeam')
                cur.execute(updateP, (None, player.id,))
                updateT = pl.updates.get('TeamMembers')
                cur.execute(updateT, (team.members - 1, team.id,))
                pl.commit(con)
                await ctx.send(f"Игрок <@{user_id}> исключен из команды {team.name}.\n"
                               f"Всего игроков в команде - {team.members}")
        else:
            await ctx.send("У вас нет прав на удаление участника из команды")

    @team.command(name="info")
    async def team_info(self, ctx, id_or_name):
        con, cur = pl.get_con_cur()
        team_id = int(id_or_name) if id_or_name.isdigit() else None
        select = pl.selects.get('teamIdName')
        cur.execute(select, (team_id, id_or_name))
        team = pl.get_team(cur.fetchone())
        if team is not None:
            embed = pl.get_team_embed(team)
        await ctx.send(embed=embed)

    @team.command(name="close")
    async def team_close(self, ctx):
        player, con, cur = pl.get_profile_by_id(pl.get_author_id(ctx))
        if player is not None:
            print(player)
            select = pl.selects.get('teamLid')
            cur.execute(select, (player.id, ))
            record = cur.fetchone()
            if record is not None:
                print(record)
                delete = pl.deletes.get("TeamLid")
                cur.execute(delete, (player.id, ))
                pl.commit(con)
                await ctx.send(f"Команда {record.name} была распущена")
            else:
                ctx.send("Вы не имеете полномочий на данную команду")

    @team.error
    @team_create.error
    @team_remove.error
    async def team_handler(self, ctx, error):
        print("Попали в обработку ошибок team")
        print(type(error))
        print(error.__class__.__name__)
        if isinstance(error, commands.errors.CommandInvokeError):
            print('Попали по адресу')
            error = error.__cause__  # получение оригинальной ошибки
            if error.pgcode == errorcodes.UNIQUE_VIOLATION:
                await ctx.send("У вас уже создана команда или существует команда с таким названием")

def setup(bot):
    bot.add_cog(Team(bot))