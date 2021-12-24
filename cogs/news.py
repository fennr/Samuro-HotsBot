import os
import sys
import yaml

import datetime
import pytz
import locale

import operator

from discord import Embed, utils, File
from discord.ext import commands
from discord_components import ComponentMessage

from pprint import pprint

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

category_name = 'Новости'
schedule_name = '📅︱расписание'
events_name = '📰︱события'
news_name = '📰︱новости'
communication_name = '💬︱общение'
event_icon = ':pushpin:'
clear = '\u200b'
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
data_type_day = '%d %B'
data_type_time = '%H:%M'
data_type = data_type_day + data_type_time
timezone = 'Europe/Moscow'
year = 2021
month_dict = {
    'Январь': 'января',
    'Февраль': 'февраля',
    'Март': 'марта',
    'Апрель': 'апреля',
    'Май': 'мая',
    'Июнь': 'июня',
    'Июль': 'июля',
    'Август': 'августа',
    'Сентябрь': 'сентября',
    'Октябрь': 'октября',
    'Ноябрь': 'ноября',
    'Декабрь': 'декабря',
}
admin_role_id = {
    'test fenrir': 880865537058545686,
    'ru hots': 703884637755408466,
}


def event_parse(ctx, emb, channel, message):
    date, time, color, full = emb.description.split('\n', maxsplit=3)
    tail, date = date.split(' ', maxsplit=1)
    date, mon = date.split(' ', maxsplit=1)
    tail, time, tail2 = time.split(' ', maxsplit=2)
    time = datetime.datetime.strptime(date + ' ' + mon + time, data_type).replace(
        year=datetime.datetime.now().year)
    weekday = time.strftime('%A')
    description = '[' + emb.title + '](https://discordapp.com/channels/' + str(ctx.guild.id) + '/' \
                  + str(channel.id) + '/' + str(message.id) + ')'
    return time, description


class News(commands.Cog, name="news"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="notify")
    async def notify(self, ctx):
        if ctx.message.author.id in config["admins"]:
            like = 'like'
            dislike = 'dislike'
            command, url = ctx.message.content.split(' ', maxsplit=1)
            link = url.split('/')
            message: ComponentMessage = await self.bot.get_guild(int(link[-3])).get_channel(
                int(link[-2])).fetch_message(int(link[-1]))
            for emb in message.embeds:
                title = emb.title
                embed = Embed(
                    title="Привет, друг",
                    description=f'Скоро начнется мероприятие [{title}]({url})\n'
                                f'Сервер: **{ctx.guild.name}**',
                    color=config['info']
                )
            reactions: list = message.reactions
            for reaction in reactions:
                print(reaction)
                print(type(reaction))
                if reaction.emoji.name != dislike:
                    async for user in reaction.users():
                        try:
                            await user.send(embed=embed)
                        except:
                            print(f"Личка пользователя {user} недоступна")
                        # print('{0} has reacted with {1.emoji}!'.format(user, reaction))
            try:
                channel = utils.get(ctx.guild.text_channels, name=communication_name)
                description = f"Скоро начнется мероприятие [{title}]({url})"
                embed = Embed(
                    title="Напоминание",
                    description=description,
                    color=config['info']
                )
                await channel.send(embed=embed)
            except:
                print('error')

    @commands.command(name="events_init")
    async def events_init(self, ctx):
        if ctx.message.author.id in config["admins"]:
            category = await ctx.guild.create_category(category_name, overwrites=None, reason=None)
            await ctx.guild.create_text_channel(schedule_name, category=category)
            await ctx.guild.create_text_channel(events_name, category=category)
            await ctx.guild.create_text_channel(news_name, category=category)
            await ctx.send("Комнаты созданы")
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await ctx.send(embed=embed)

    @commands.command(name="am")
    async def am(self, ctx):
        if ctx.message.author.id in config["admins"]:
            command, text = ctx.message.content.split(' ', maxsplit=1)
            await ctx.message.delete()
            await ctx.send(text)

    @commands.command(name="pm")
    async def pm(self, ctx):
        server_name = {
            'test': 'Fenrir︱Test',
            'ruhots': 'RU︱Heroes of the Storm',
            'lounge': 'RU︱Heroes of the Storm',
            'kato': 'Awokato game',
            'dung_h': 'Dungeon Шмэтокрыла',
            'dung_m': 'Dungeon Шмэтокрыла',
            'stlk': 'STLK',
        }
        server_rooms = {
            'test': 845658540341592099,
            'ruhots': 642853714515722241,
            'lounge': 886270709393928242,
            'kato': 835521779521814538,
            'dung_h': 858455796412710922,
            'dung_m': 472534563479093269,
            'stlk': 124864790110797824,
        }
        if ctx.message.author.id in config["admins"]:
            command, short_server_name, message = ctx.message.content.split(' ', maxsplit=2)
            for guild in self.bot.guilds:
                if short_server_name == 'all' and ctx.guild.name in server_name.values():
                    for room in server_rooms.values():
                        try:
                            channel = guild.get_channel(room)
                            await channel.send(message)
                        except:
                            pass
                else:
                    server = server_name.setdefault(short_server_name)
                    if guild.name == server:
                        room = server_rooms.setdefault(short_server_name)
                        print(room)
                        if room is not None:
                            channel = guild.get_channel(room)
                            print(channel)
                            print(type(channel))
                            if channel is not None:
                                await channel.send(message)
                                break

    @commands.command(name="add_news")
    async def add_news(self, ctx):
        role = utils.find(lambda r: r.id in admin_role_id.values(), ctx.message.guild.roles)
        if ctx.message.author.id in config["admins"] or role in ctx.message.author.roles:
            command, header, color, description = ctx.message.content.split('\n', maxsplit=3)
            color = int(color, 16)
            embed = Embed(
                title=header,
                description=description,
                color=color
            )
            channel = utils.get(ctx.guild.text_channels, name=news_name)
            if len(ctx.message.attachments) > 0:
                attachment = ctx.message.attachments[0]
                if attachment.filename.endswith(".jpg") or attachment.filename.endswith(
                        ".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(
                    ".webp") or attachment.filename.endswith(".gif"):
                    image = attachment.url
                elif "https://images-ext-1.discordapp.net" in ctx.message.content or "https://tenor.com/view/" in ctx.message.content:
                    image = ctx.message.content
                embed.set_image(url=image)
            await channel.send(embed=embed)

    @commands.command(name="add_event")
    async def add_event(self, ctx):
        role = utils.find(lambda r: r.id in admin_role_id.values(), ctx.message.guild.roles)
        if ctx.message.author.id in config["admins"] or role in ctx.message.author.roles:
            try:
                news_data = ctx.message.content.split('\n', maxsplit=4)
                news_data = news_data[1:]
                description = ''
                news_header = news_data.pop(0)
                news_time = datetime.datetime.strptime(news_data.pop(0), '%m/%d %H:%M')
                new_day = str(news_time.strftime(data_type_day))
                new_time = str(news_time.strftime(data_type_time))
                new_day, new_month = new_day.split(' ', maxsplit=1)
                # new_month = month_dict[new_month]
                color = news_data.pop(0)
                news_full = news_data.pop(0)
                description += '**Дата:** ' + new_day + ' ' + new_month + '\n' + '**Время:** ' + new_time + ' по МСК\n' + \
                               '\n' + news_full
                color = int(color, 16)
                embed = Embed(
                    title=news_header,
                    description=description,
                    color=color
                )
                data = None
                channel = utils.get(ctx.guild.text_channels, name=events_name)
                if len(ctx.message.attachments) > 0:
                    attachment = ctx.message.attachments[0]
                    if attachment.filename.endswith(".jpg") or attachment.filename.endswith(
                            ".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(
                        ".webp") or attachment.filename.endswith(".gif"):
                        image = attachment.url
                    elif "https://images-ext-1.discordapp.net" in ctx.message.content or "https://tenor.com/view/" in ctx.message.content:
                        image = ctx.message.content
                    embed.set_image(url=image)
                    '''async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status != 200:
                                return await channel.send('Could not download file...')
                            data = io.BytesIO(await resp.read())'''
                # await ctx.message.delete()
                await channel.send(embed=embed)
                await News.update_schedule(self, ctx, clear_message=False)
            except:
                description = 'Введите описание ивента в следующем формате: \n' \
                              '#add_event\n ' \
                              'Заголовок\n ' \
                              'Время в формате %m/%d %H:%M \n' \
                              'Шестнадцаритичный код цвета для сообщения \n' \
                              'Полное описание ивента любой длины\n------\n ' \
                              'После корректной генерации ивента некорректные сообещния будут зачищены'
                embed = Embed(
                    title='Ошибка при вводе',
                    description=description,
                    color=config["error"]
                )
                await ctx.send(embed=embed)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await ctx.send(embed=embed)

    @commands.command(name="update_events")
    async def update_events(self, ctx, clear_message=True):
        if clear_message:
            await ctx.message.delete()
        channel = utils.get(ctx.guild.text_channels, name=events_name)
        messages = await channel.history(limit=200).flatten()
        now = datetime.datetime.strptime(datetime.datetime.today().strftime(data_type), data_type) \
                  .replace(year=datetime.datetime.now().year) + datetime.timedelta(hours=3)
        for message in messages:
            for emb in message.embeds:
                time, description = event_parse(ctx, emb, channel, message)
                # print(f"now: {now}\ntime: {time}")
                if now > time:
                    await message.delete()

    @commands.command(name="clear_events")
    async def clear_events(self, ctx):
        error_color = '#e02b2b'
        channel = utils.get(ctx.guild.text_channels, name=events_name)
        messages = await channel.history(limit=200).flatten()
        # pprint(messages)
        for message in reversed(messages):
            if not message.author.bot:
                await message.delete()
            for emb in message.embeds:
                if str(emb.color) == error_color:
                    await message.delete()

    @commands.command(name="update_schedule")
    async def update_schedule(self, ctx, clear_message=True):
        img = None
        img_path = 'img/'
        print(ctx.guild.name)
        if ctx.guild.name == 'RU︱Heroes of the Storm':
            img_name = 'scheduleHots.png'
            color = config["info"]
        elif ctx.guild.name == 'RU︱Hearthstone':
            img_name = 'scheduleHS.png'
            color = int('DBC31E', 16)
        else:
            img_name = 'scheduleHS.png'
            color = config["info"]
        if clear_message:
            pass
            # await ctx.message.delete()
        await News.clear_events(self, ctx)
        await News.update_events(self, ctx, clear_message=False)
        # try:
        channel = utils.get(ctx.guild.text_channels, name=schedule_name)
        messages = await channel.history(limit=200).flatten()
        for message in messages:
            await message.delete()
        img = File(img_path + img_name)
        img.filename = img_name
        channel = utils.get(ctx.guild.text_channels, name=events_name)
        messages = await channel.history(limit=200).flatten()
        embed = Embed(
            title='Ближайшие события:',
            color=color
        )
        events = []
        for message in reversed(messages):
            description = ''
            for emb in message.embeds:
                time, description = event_parse(ctx, emb, channel, message)
                events.append(dict(time=time, description=description))
        events.sort(key=operator.itemgetter('time'))
        for event in events:
            date = event['time'].strftime('%d')
            mon = event['time'].strftime('%B')
            weekday = event['time'].strftime('%A')
            embed.add_field(
                name=f"\u200b",
                value=f"{event_icon} {event['description']} — {date} {mon} ({weekday})",
                inline=False
            )
        if len(events) == 0:
            embed.add_field(
                name=f"\u200b",
                value=f"В текущий момент нет запланированных событий на сервере",
                inline=False
            )
        embed.set_image(url=f'attachment://{img_name}')
        '''except:
            embed = Embed(
                title='Ошибка чтения новостей',
                description='Удалите сообщения в событиях созданные вручную и добавьте ивенты через #add_event',
                color=config["error"]
            )'''
        channel = utils.get(ctx.guild.text_channels, name=schedule_name)
        if img is not None:
            await channel.send(embed=embed, file=img)
        else:
            await channel.send(embed=embed)

    @commands.command(name="test1")
    async def test1(self, ctx, *args):
        if ctx.message.author.id in config["owners"]:
            if len(args) == 0:
                await ctx.send('Добавьте описание новости после команды')
            else:
                description = ' '.join(args)
                embed = Embed(
                    title='Новая новость',
                    description=description,
                    color=config["info"]
                )
                embed.set_footer(
                    text=f"От пользователя {ctx.author}"
                )
                owner = self.bot.get_user(int(config["owner"]))
                # check if dm exists, if not create it
                if owner.dm_channel is None:
                    await owner.create_dm()
                # if creation of dm successful
                if owner.dm_channel is not None:
                    await owner.dm_channel.send(embed=embed)
                    message = 'Спасибо. Сообщение было отправлено'
                    await ctx.send(message)


def setup(bot):
    bot.add_cog(News(bot))
