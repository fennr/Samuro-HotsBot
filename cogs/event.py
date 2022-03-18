import pytz
from datetime import datetime
from discord import Embed, utils, Member
from discord.ext import commands
from utils.library import base, profile as pl
from utils import check
from discord_slash import cog_ext, SlashContext
import asyncio

config = base.get_config()

guild_ids = [845658540341592096]  # Сервер ID для тестирования


async def event_report(ctx, text):
    if ctx.guild_id == 642852514865217578:  # RU Hots
        channel_id = 879385907923390464
    else:
        channel_id = 946304981475151902
    channel = utils.get(ctx.guild.channels, id=channel_id)
    message = f"Сообщение от пользователя {ctx.author.mention}:\n{text}"
    await channel.send(message)
    await ctx.send("Сообщение отправлено администрации", hidden=True)



class Event(commands.Cog, name="Event"):
    """
    — Модуль работы с ивентами
    """

    #votes_blue = set()
    #votes_red = set()

    def __init__(self, bot):
        self.bot = bot
        self.votes_blue = set()
        self.votes_red = set()

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

    @event.command(name="poll")
    @check.is_lead()
    async def event_poll(self, ctx, *, delay=240.0):
        """
        — Создание голосования на победу
        """
        blue = '🟦'
        red = '🟥'
        poll_title = "Кто победит?"
        embed = Embed(
            title=f"{poll_title}",
            # description=f"{poll_title}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"4 минуты на голосование"
        )
        embed_message = await ctx.send(embed=embed)
        await embed_message.add_reaction(blue)
        await embed_message.add_reaction(red)
        await asyncio.sleep(delay)
        await embed_message.remove_reaction(blue, member=embed_message.author)
        await embed_message.remove_reaction(red, member=embed_message.author)
        message = await ctx.channel.fetch_message(embed_message.id)
        #print(message.reactions)
        blue_bet = []
        red_bet = []
        for reaction in message.reactions:
            if reaction.emoji == blue:
                async for user in reaction.users():
                    blue_bet.append(user.mention)
            if reaction.emoji == red:
                async for user in reaction.users():
                    red_bet.append(user.mention)
        self.votes_blue = set(blue_bet) - set(red_bet)
        self.votes_red = set(red_bet) - set(blue_bet)
        await embed_message.delete()
        await ctx.send(f"Голосование завершено")

    @event.command(name="poll_end")
    async def event_poll_end(self, ctx, winner):

        text_blue = ', '.join(self.votes_blue)
        text_red = ', '.join(self.votes_red)
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
        self.votes_blue = set()
        self.votes_red = set()

    @event.command(name="5x5")
    @check.is_lead()
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
    @check.is_lead()
    async def event_winner(self, ctx, winner=None, delta=6, points=1):
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
                pl.team_change_stats(team=win_team, guild_id=guild_id)
                await ctx.send(f"Очки за победу начислены")
                pl.team_change_stats(team=lose_team, guild_id=guild_id, winner=False)
                await ctx.send(f"Очки за поражение начислены")
                await ctx.send(f"Матч успешно закрыт")
                await self.event_poll_end(ctx, winner)
            else:
                await ctx.send(f"Открытых матчей не найдено")
            pl.commit(con)
        else:
            await ctx.send(f"Укажите победителя *red* или *blue*")

    @event.command(name="remove")
    @check.is_lead()
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
            self.votes_blue = set()
            self.votes_red = set()
        else:
            await ctx.send(f"В этой комнате нет открытых матчей")

    @cog_ext.cog_slash(name="report", description="Репорт за слив игры в 5x5")
    async def event_report1(self, ctx: SlashContext, text):
        await event_report(ctx, text)

    @cog_ext.cog_slash(name="репорт", description="Репорт за слив игры в 5x5")
    async def event_report2(self, ctx: SlashContext, text):
        await event_report(ctx, text)


def setup(bot):
    bot.add_cog(Event(bot))
