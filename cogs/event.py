""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import pytz
from datetime import datetime
import discord
from discord import Embed, utils, Member
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import utils.library.embeds
import utils.library.profile
from utils.classes import Const
from utils import exceptions, sql, library, check
import asyncio
from utils.classes.Const import config

guild_ids = [845658540341592096]  # Сервер ID для тестирования


async def event_report(ctx, text):
    if ctx.guild_id == 642852514865217578:  # RU Hots
        channel_id = 848504279513956372
    else:
        channel_id = 880863858653286401
    channel = discord.utils.get(ctx.guild.channels, id=channel_id)
    message = f"Сообщение от пользователя {ctx.author.mention}:\n{text}"
    await channel.send(message)
    await ctx.send("Сообщение отправлено администрации", hidden=True)


async def insert_votes(ctx, cur, record, one, two):
    votes = set(one) - set(two)
    for user_id in votes:
        member = ctx.guild.get_member(user_id)
        if discord.utils.get(member.roles, id=Const.events.role_id):
            await ctx.send(f"Предупреждение игроку {member.mention} за попытку голосования")
        else:
            insert = Const.inserts.Votes
            cur.execute(insert, (user_id, record.event_id, Const.events.blue))


class Event(commands.Cog, name="Event"):
    """
    — Модуль работы с ивентами
    """

    # votes_blue = set()
    # votes_red = set()

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
    @check.is_lead()
    async def event_test(self, ctx, *, avamember: Member = None):
        await ctx.send('Тест прав на ивенты пройден')

    @event.command(name="role")
    @check.is_lead()
    async def event_role(self, ctx):
        ctx.guild.get()

    @event.command(name="poll")
    @check.is_lead()
    async def event_poll(self, ctx, *, delay=5.0):
        """
        — Создание голосования на победу
        """
        con, cur = library.get.con_cur()
        select = Const.selects.EHActive
        cur.execute(select, (ctx.channel.id, True))
        record = cur.fetchone()
        if record is None:
            raise exceptions.NoActiveEvents
        blue = '🟦'
        red = '🟥'
        poll_title = "Кто победит?"
        guild_id = library.get.guild_id(ctx)
        embed = Embed(
            title=f"{poll_title}",
            # description=f"{poll_title}",
            color=config.success
        )
        embed.set_footer(
            text=f"5 минут на голосование"
        )
        embed_message = await ctx.send(embed=embed)
        try:
            await embed_message.add_reaction(blue)
            await embed_message.add_reaction(red)
            await ctx.message.delete()
            await asyncio.sleep(delay)
            await embed_message.remove_reaction(blue, member=embed_message.author)
            await embed_message.remove_reaction(red, member=embed_message.author)
            message = await ctx.channel.fetch_message(embed_message.id)
            select = Const.selects.EHActive
            cur.execute(select, (ctx.channel.id, True))
            record = cur.fetchone()
            if record is None:
                raise exceptions.NoActiveEvents
            blue_bet = []
            red_bet = []
            for reaction in message.reactions:
                if reaction.emoji == blue:
                    async for user in reaction.users():
                        blue_bet.append(user.id)
                if reaction.emoji == red:
                    async for user in reaction.users():
                        red_bet.append(user.id)
            await insert_votes(ctx, cur, record, blue_bet, red_bet)
            await insert_votes(ctx, cur, record, red_bet, blue_bet)
            library.commit(con)
            await embed_message.delete()
            await ctx.send(f"Голосование завершено")
        except Exception as e:
            await embed_message.delete()
            print(e)
            print("Ошибка при создании голосования")
            await ctx.send(e)

    @event.command(name="poll_end")
    async def event_poll_end(self, ctx, winner, event_id):
        con, cur = library.get.con_cur()
        select = Const.selects.VotesEvent
        cur.execute(select, (event_id,))
        records = cur.fetchall()
        text_blue = ''
        text_red = ''
        for record in records:
            con, cur = library.get.con_cur()
            if record.vote == winner:
                correct = 1
                wrong = 0
            else:
                correct = 0
                wrong = 1
            select = '''SELECT * FROM "VoteStats" WHERE id = %s'''
            cur.execute(select, (record.id,))
            r = cur.fetchone()
            if r is None:
                insert = '''INSERT INTO "VoteStats"(id, correct, wrong) VALUES (%s, %s, %s)'''
                cur.execute(insert, (record.id, correct, wrong))
            else:
                update = '''UPDATE "VoteStats" SET correct = %s, wrong = %s WHERE id = %s'''
                cur.execute(update, (r.correct + correct, r.wrong + wrong,
                                     record.id))
            delete = '''DELETE FROM "Votes" WHERE id = %s AND event_id = %s'''
            cur.execute(delete, (record.id, record.event_id))
            library.commit(con)
            if record.vote == 'blue':
                text_blue += f"{library.get.mention(record.id)} "
            else:
                text_red += f"{library.get.mention(record.id)} "

        if winner == 'blue':
            await ctx.send(f"Победила команда **синих**")
            if len(text_blue) > 0:
                await ctx.send(f"За победу **синих** проголосовали: {text_blue}")
            if len(text_red) > 0:
                await ctx.send(f"За победу красных проголосовали: {text_red}")
        if winner == 'red':
            await ctx.send(f"Победила команда **красных**")
            if len(text_red) > 0:
                await ctx.send(f"За победу **красных** проголосовали: {text_red}")
            if len(text_blue) > 0:
                await ctx.send(f"За победу синих проголосовали: {text_blue}")

    @event.command(name="5x5")
    @check.is_lead()
    async def event_5x5(self, ctx, *args):
        """
        @ x 10 - создать 5х5 на 10 человек
        """
        if len(args) != 10:
            await ctx.send("Введите 10 участников")
        else:
            con, cur = library.get.con_cur()
            guild_id = library.get.guild_id(ctx)
            room_id = ctx.channel.id
            admin = library.get.author(ctx)
            players = []
            bad_flag = False
            for name in args:
                user_id = library.get.user_id(name)
                select = Const.selects.PlayersIdOrBtag
                cur.execute(select, (user_id, name))
                player = library.get.player(cur.fetchone())
                if player is not None:
                    players.append(player)
                else:
                    bad_flag = True
                    await ctx.send(f"Участника {name} нет в базе")
            if not bad_flag:
                select = Const.selects.EHActive
                cur.execute(select, (room_id, True))
                record = cur.fetchone()
                if record is None:
                    players.sort(key=utils.library.profile.sort_by_mmr, reverse=True)
                    # обработка на случай одинакового ммр
                    unique_mmr = []
                    for player in players:
                        await library.add_role(ctx, player, message=False)  # добавление роли 5х5 если она есть
                        while player.mmr in unique_mmr:
                            player.mmr = float(player.mmr) + 0.1
                        unique_mmr.append(player.mmr)
                    team_one_mmr, team_two_mmr = library.min_diff_sets(
                        [float(player.mmr) for index, player in enumerate(players[:-2])])
                    team_one_mmr += (float(players[-1].mmr),)
                    team_two_mmr += (float(players[-2].mmr),)
                    team_one = [player for player in players if float(player.mmr) in team_one_mmr]
                    team_two = [player for player in players if float(player.mmr) in team_two_mmr]
                    #print(team_one)
                    now = str(datetime.now(pytz.timezone('Europe/Moscow')))[:19]
                    insert = Const.inserts.Event
                    cur.execute(insert, (now, admin, guild_id, True, room_id,  # ctx.message.author.name
                                         team_one[0].btag, team_one[1].btag, team_one[2].btag, team_one[3].btag,
                                         team_one[4].btag,
                                         team_two[0].btag, team_two[1].btag, team_two[2].btag, team_two[3].btag,
                                         team_two[4].btag))
                    library.commit(con)
                    team_one_discord = ' '.join([library.get.player_data(player) for player in team_one])
                    team_two_discord = ' '.join([library.get.player_data(player) for player in team_two])
                    await ctx.send(f"**Синяя команда:** \n{team_one_discord}")
                    await ctx.send(f"**Красная команда:** \n{team_two_discord}")  # mean(team_blue):.2f
                else:
                    await ctx.send(f"Для создания нового матча завершите предыдущий")

    @event.command(name="1x4")
    @check.is_lead()
    async def event_1x4(self, ctx, *args):
        """
        - Смертокрыл против героев
        """
        if len(args) != 5:
            await ctx.send("Введите 5 участников")
        else:
            con, cur = library.get.con_cur()
            guild_id = library.get.guild_id(ctx)
            room_id = ctx.channel.id
            admin = library.get.author(ctx)
            players = []
            bad_flag = False
            for name in args:
                user_id = library.get.user_id(name)
                select = Const.selects.PlayersIdOrBtag
                cur.execute(select, (user_id, name))
                player = library.get.player(cur.fetchone())
                if player is not None:
                    players.append(player)
                else:
                    bad_flag = True
                    await ctx.send(f"Участника {name} нет в базе")
            if not bad_flag:
                select = Const.selects.EHActive
                cur.execute(select, (room_id, True))
                record = cur.fetchone()
                if record is None:
                    deathwing = players[0]
                    heroes = players[1:]
                    team_heroes = ' '.join([library.get.player_data(player) for player in heroes])
                    await ctx.send(f"**Синяя команда:** \n{deathwing}")
                    await ctx.send(f"**Красная команда:** \n{team_heroes}")  # mean(team_blue):.2f



    @event.command(name="winner")
    @check.is_lead()
    async def event_winner(self, ctx, winner=None, delta=6, points=1):
        """
        red | blue - выбрать победителя
        """
        if winner == 'blue' or winner == 'red':
            con, cur = library.get.con_cur()
            room_id = ctx.channel.id
            guild_id = library.get.guild_id(ctx)
            select = Const.selects.EHActive
            cur.execute(select, (room_id, True))
            record = cur.fetchone()
            if record is not None:
                if winner == 'blue':
                    win_team = [record.blue1, record.blue2, record.blue3, record.blue4, record.blue5]
                    lose_team = [record.red1, record.red2, record.red3, record.red4, record.red5]
                else:  # red
                    lose_team = [record.blue1, record.blue2, record.blue3, record.blue4, record.blue5]
                    win_team = [record.red1, record.red2, record.red3, record.red4, record.red5]
                update = Const.updates.EHWinner
                cur.execute(update, (winner, delta, points, False,
                                     room_id, True))
                await library.team_change_stats(ctx, team=win_team, delta=delta, guild_id=guild_id)
                await ctx.send(f"Очки за победу начислены")
                await library.team_change_stats(ctx, team=lose_team, delta=delta, guild_id=guild_id, winner=False)
                await ctx.send(f"Очки за поражение начислены")
                try:
                    await self.event_poll_end(ctx, winner, record.event_id)
                except Exception as e:
                    print(e)
                    print(f"Ошибка закрытия голосования")
            else:
                await ctx.send(f"Открытых матчей не найдено")
            library.commit(con)
            await ctx.send(f"Матч успешно закрыт")
        else:
            await ctx.send(f"Укажите победителя *red* или *blue*")

    @event.command(name="remove")
    @check.is_lead()
    async def event_remove(self, ctx):
        """
        - Отменить матч
        """
        con, cur = library.get.con_cur()
        room_id = ctx.channel.id
        delete = Const.deletes.EventActive
        cur.execute(delete, (room_id, True))
        try:  # Зачистка роли
            record = cur.fetchone()
            for btag in record:
                player = library.get.profile_by_id_or_btag(btag)
                await library.remove_role(ctx, player)
        except Exception as e:
            print(e)
            print("Нет роли 5x5")
        library.commit(con)
        if cur.rowcount:  # счетчик записей, найдет 1 или 0
            await ctx.send(f"Активный матч был отменен, можно пересоздать команды")
        else:
            await ctx.send(f"В этой комнате нет открытых матчей")

    @event.command(name="msg")
    @check.is_samuro_dev()
    async def event_msg(self, ctx, user_id, *message):
        msg = ' '.join(message)
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(msg)
        except:
            pass

    @cog_ext.cog_slash(name="report", description="Репорт за слив игры в 5x5")
    async def event_report1(self, ctx: SlashContext, text):
        await event_report(ctx, text)

    @cog_ext.cog_slash(name="репорт", description="Репорт за слив игры в 5x5")
    async def event_report2(self, ctx: SlashContext, text):
        await event_report(ctx, text)

    @event_poll.error
    async def event_handler(self, ctx, error):
        # print("Обработка ошибок heroes")
        error = getattr(error, 'original', error)  # получаем пользовательские ошибки
        print(error)
        # print(type(error))
        print(f"Сообщение вызвавшее ошибку: '{ctx.message.content}' guild {ctx.guild} by {ctx.author}")

        if isinstance(error, exceptions.NoActiveEvents):
            await ctx.send(f"Ошибка голосования. В комнате нет активных игр")


def setup(bot):
    bot.add_cog(Event(bot))
