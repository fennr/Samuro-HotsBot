import os
import yaml
import psycopg2.extras
import pytz
from datetime import datetime
from discord import Embed, utils, Member
from discord.ext import commands
from helpers import sql, check
from helpers import profile_lib as pl
from discord_slash import cog_ext, SlashContext

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

guild_ids = [845658540341592096]  # Сервер ID для тестирования




class Event(commands.Cog, name="event"):
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
        """
        @ x 10 - создать 5х5 на 10 человек
        """
        if len(args) != 10:
            await ctx.send("Введите 10 участников турнира")
        else:
            con, cur = pl.get_con_cur()
            guild_id = pl.get_guild_id(ctx)
            room_id = ctx.channel.id
            admin = pl.get_author(ctx)
            players = []
            bad_flag = False
            for name in args:
                user_id = pl.get_user_id(name)
                select = pl.selects.get('PlayersIdOrBtag')
                cur.execute(select, (user_id, name))
                player = pl.get_player(cur.fetchone())
                if player is not None:
                    players.append(player)
                else:
                    bad_flag = True
                    await ctx.send(f"Участника {name} нет в базе")
            if not bad_flag:
                select = pl.selects.get('ehActive')
                cur.execute(select, (room_id, True))
                record = cur.fetchone()
                if record is None:
                    players.sort(key=pl.sort_by_mmr, reverse=True)
                    # обработка на случай одинакового ммр
                    unique_mmr = []
                    for player in players:
                        while player.mmr in unique_mmr:
                            player.mmr = float(player.mmr) + 0.1
                        unique_mmr.append(player.mmr)
                    team_one_mmr, team_two_mmr = pl.min_diff_sets(
                        [float(player.mmr) for index, player in enumerate(players[:-2])])
                    team_one_mmr += (float(players[-1].mmr),)
                    team_two_mmr += (float(players[-2].mmr),)
                    team_one = [player for player in players if float(player.mmr) in team_one_mmr]
                    team_two = [player for player in players if float(player.mmr) in team_two_mmr]
                    print(team_one)
                    now = str(datetime.now(pytz.timezone('Europe/Moscow')))[:19]
                    insert = '''INSERT INTO "EventHistory"(time, admin, guild_id, active, room_id, 
                    blue1, blue2, blue3, blue4, blue5, 
                    red1, red2, red3, red4, red5)
                    VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s )'''
                    cur.execute(insert, (now, admin, guild_id, True, room_id,  # ctx.message.author.name
                                         team_one[0].btag, team_one[1].btag, team_one[2].btag, team_one[3].btag,
                                         team_one[4].btag,
                                         team_two[0].btag, team_two[1].btag, team_two[2].btag, team_two[3].btag,
                                         team_two[4].btag))
                    pl.commit(con)
                    team_one_discord = ' '.join([pl.get_player_data(player) for player in team_one])
                    team_two_discord = ' '.join([pl.get_player_data(player) for player in team_two])
                    await ctx.send(f"**Синяя команда:** \n{team_one_discord}")
                    await ctx.send(f"**Красная команда:** \n{team_two_discord}")  # mean(team_blue):.2f
                else:
                    await ctx.send(f"Для создания нового матча завершите предыдущий")

    @event.command(name="winner")
    @check.is_admin()
    async def event_winner(self, ctx, winner=None, delta=7, points=1):
        """
        red | blue - выбрать победителя
        """
        if winner == 'blue' or winner == 'red':
            con, cur = pl.get_con_cur()
            room_id = ctx.channel.id
            guild_id = pl.get_guild_id(ctx)
            select = pl.selects.get('ehActive')
            cur.execute(select, (room_id, True))
            record = cur.fetchone()
            if record is not None:
                if winner == 'blue':
                    win_team = [record.blue1, record.blue2, record.blue3, record.blue4, record.blue5]
                    lose_team = [record.red1, record.red2, record.red3, record.red4, record.red5]
                elif winner == 'red':
                    lose_team = [record.blue1, record.blue2, record.blue3, record.blue4, record.blue5]
                    win_team = [record.red1, record.red2, record.red3, record.red4, record.red5]
                update = '''UPDATE "EventHistory" SET winner = %s, delta_mmr = %s, points = %s,
                                              active = %s 
                            WHERE room_id = %s AND active = %s'''
                cur.execute(update, (winner, delta, points, False,
                                     room_id, True))
                await ctx.send(f"Матч успешно закрыт")
                pl.team_change_stats(team=win_team, guild_id=guild_id)
                await ctx.send(f"Очки за победу начислены")
                pl.team_change_stats(team=lose_team, guild_id=guild_id, winner=False)
                await ctx.send(f"Очки за поражение начислены")
            else:
                await ctx.send(f"Открытых матчей не найдено")
            pl.commit(con)
        else:
            await ctx.send(f"Укажите победителя *red* или *blue*")

    @event.command(name="remove")
    @check.is_admin()
    async def event_remove(self, ctx):
        """
        - Отменить матч
        """
        con, cur = pl.get_con_cur()
        room_id = ctx.channel.id
        delete = '''DELETE FROM "EventHistory" WHERE room_id = %s AND active = %s'''
        cur.execute(delete, (room_id, True))
        pl.commit(con)
        if cur.rowcount:  # счетчик записей, найдет 1 или 0
            await ctx.send(f"Активный матч был отменен, можно пересоздать команды")
        else:
            await ctx.send(f"В этой комнате нет открытых матчей")


    async def event_report(self, ctx, text):
        if ctx.guild_id == 642852514865217578:  # RU Hots
            channel_id = 879385907923390464
        else:
            channel_id = 946304981475151902
        channel = utils.get(ctx.guild.channels, id=channel_id)
        message = f"Сообщение от пользователя {ctx.author.mention}:\n{text}"
        await channel.send(message)
        await ctx.send("Сообщение отправлено администрации", hidden=True)


    @cog_ext.cog_slash(name="report", description="Репорт за слив игры в 5x5")
    async def event_report1(self, ctx: SlashContext, text):
        await self.event_report(ctx, text)

    @cog_ext.cog_slash(name="репорт", description="Репорт за слив игры в 5x5")
    async def event_report2(self, ctx: SlashContext, text):
        await self.event_report(ctx, text)


def setup(bot):
    bot.add_cog(Event(bot))
