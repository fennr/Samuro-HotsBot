from discord import Colour
from discord.ext import commands
from discord.utils import get
from psycopg2 import errorcodes, errors
from utils.classes import Const
from utils import exceptions, sql, library, check

config = library.get_yaml()

UniqueViolation = errors.lookup(errorcodes.UNIQUE_VIOLATION)


class Team(commands.Cog, name="Team"):
    """
    — Модуль работы с Командами/Кланами
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="team")
    async def team(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @team.command(name="create")
    @check.is_admin()
    async def team_create(self, ctx, leader, team_name, color=Colour.random()):
        '''
        — Создает команду team_name
        '''
        con, cur = library.get.con_cur()
        print(leader)
        player = library.get.profile_by_id_or_btag(leader)
        if player is not None:
            insert = Const.inserts.Team
            cur.execute(insert, (team_name, player.id))
            team_id = cur.fetchone()[0]
            update = Const.updates.PlayerTeam
            cur.execute(update, (team_id, player.id))
            library.commit(con)
            await ctx.send(f"Команда {team_name} создана")
            print(color)
            await ctx.guild.create_role(name=team_name, color=color)
            member = ctx.guild.get_member(player.id)
            role = get(member.guild.roles, name=team_name)
            await member.add_roles(role)
        else:
            print("Для использования команды добавьте Ваш профиль в базу")

    @team.command(name="add")
    async def team_add(self, ctx, user):
        """
        — Добавить в команду игрока @user
        """
        con, cur = library.get.con_cur()
        user_id = library.get.author_id(ctx)
        select = Const.selects.TeamLid
        cur.execute(select, (user_id, ))
        team = library.get.team(cur.fetchone())
        if team is not None:
            player = library.get.profile_by_id_or_btag(user)
            if player.team is None:
                updateP = Const.updates.PlayerTeam
                print(team.id)
                print(player.id)
                cur.execute(updateP, (team.id, player.id, ))
                updateT = Const.updates.TeamMembers
                cur.execute(updateT, (team.members+1, team.id, ))
                library.commit(con)
                await ctx.send(f"Игрок <@{player.id}> добавлен в команду {team.name}\n"
                               f"Всего игроков в команде - {team.members+1}")
                member = ctx.guild.get_member(player.id)
                role = get(member.guild.roles, name=team.name)
                await member.add_roles(role)
            else:
                await ctx.send("Игрок уже в команде. Возможно состоять только в одной команде")
        else:
            await ctx.send("У вас нет прав на добавление участников в команду")

    @team.command(name="remove")
    async def team_remove(self, ctx, user):
        """
        — Удалить из команды @user
        """
        con, cur = library.get.con_cur()
        user_id = library.get.author_id(ctx)
        select = Const.selects.TeamLid
        cur.execute(select, (user_id, ))
        team = library.get.team(cur.fetchone())
        print(team)
        if team is not None:
            player = library.get.profile_by_id_or_btag(user)
            print(player)
            if player.team is not None:
                updateP = Const.updates.PlayerTeam
                cur.execute(updateP, (None, player.id,))
                updateT = Const.updates.TeamMembers
                cur.execute(updateT, (team.members - 1, team.id,))
                library.commit(con)
                await ctx.send(f"Игрок {library.get.mention(player.id)} исключен из команды {team.name}\n"
                               f"Всего игроков в команде - {team.members - 1}")
                member = ctx.guild.get_member(player.id)
                role = get(member.guild.roles, name=team.name)
                await member.remove_roles(role)
            else:
                await ctx.send("Игрок не состоит в команде")
        else:
            await ctx.send("У вас нет прав на удаление участника из команды")

    @team.command(name="info")
    async def team_info(self, ctx, id_or_name):
        """
        — Информация о команде по имени или ID
        """
        con, cur = library.get.con_cur()
        team_id = int(id_or_name) if id_or_name.isdigit() else None
        select = Const.selects.TeamIdName
        cur.execute(select, (team_id, id_or_name))
        team = library.get.team(cur.fetchone())
        if team is not None:
            embed = library.profile.get_team_embed(team)
            await ctx.send(embed=embed)

    @team.command(name="close")
    async def team_close(self, ctx):
        con, cur = library.get.con_cur()
        player = library.get.profile_by_id_or_btag(library.get.author_id(ctx))
        if player is not None:
            print(player)
            select = Const.selects.TeamLid
            cur.execute(select, (player.id, ))
            record = cur.fetchone()
            if record is not None:
                print(record)
                delete = Const.deletes.TeamLid
                cur.execute(delete, (player.id, ))
                pl.commit(con)
                await ctx.send(f"Команда {record.name} была распущена")
                role = get(ctx.message.guild.roles, name=record.name)
                if role:
                    await role.delete()
                await ctx.guild.delete_role(ctx.guild, name=record.name)
            else:
                ctx.send("Вы не имеете полномочий на данную команду")

    @team.error
    @team_create.error
    @team_remove.error
    async def team_handler(self, ctx, error):
        print("Попали в обработку ошибок team")
        error = getattr(error, 'original', error)  # получаем пользовательские ошибки
        print(type(error))
        print(error)
        if isinstance(error, UniqueViolation):
            await ctx.send("У вас уже создана команда или существует команда с таким названием")


def setup(bot):
    bot.add_cog(Team(bot))