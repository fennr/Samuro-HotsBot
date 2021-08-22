import os
import sys
import yaml

import datetime
import locale

from discord import Embed, utils
from discord.ext import commands

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
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
data_type_day = '%d %B'
data_type_time = '%H:%M'
data_type = data_type_day + data_type_time
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

class News(commands.Cog, name="news"):
    def __init__(self, bot):
        self.bot = bot

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


    @commands.command(name="add_news")
    async def add_news(self, ctx):
        command, header, description = ctx.message.content.split('\n', maxsplit=2)
        embed = Embed(
            title=header,
            description=description,
            color=config["info"]
        )
        await ctx.message.delete()
        channel = utils.get(ctx.guild.text_channels, name=news_name)
        await channel.send(embed=embed)

    @commands.command(name="add_event")
    async def add_event(self, ctx):
        if ctx.message.author.id in config["admins"]:
            #try:
            news_data = ctx.message.content.split('\n', maxsplit=4)
            news_data = news_data[1:]
            description = ''
            news_header = news_data.pop(0)
            news_time = datetime.datetime.strptime(news_data.pop(0), '%m/%d %H:%M')
            new_day = str(news_time.strftime(data_type_day))
            new_time = str(news_time.strftime(data_type_time))
            new_day, new_month = new_day.split(' ', maxsplit=1)
            #new_month = month_dict[new_month]
            news_short = news_data.pop(0)
            news_full = news_data.pop(0)
            description += '**Дата:** ' + new_day + ' ' + new_month + '\n' + '**Время:** ' + new_time + ' по МСК\n' + \
                           '\n' + news_full
            color = int(news_short, 16)
            embed = Embed(
                title=news_header,
                description=description,
                color=color
            )
            if len(ctx.message.attachments) > 0:
                embed.set_image(url=ctx.message.attachments[0])
            await ctx.message.delete()
            await News.clear_events(self, ctx)
            channel = utils.get(ctx.guild.text_channels, name=events_name)
            await channel.send(embed=embed)
            await News.clear_schedule(self, ctx, clear_message=False)
            await News.update_schedule(self, ctx, add_event=True)
            '''except:
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
                await ctx.send(embed=embed)'''
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await ctx.send(embed=embed)

    @commands.command(name="clear_schedule")
    async def clear_schedule(self, ctx, clear_message=True):
        if clear_message:
            await ctx.message.delete()
        channel = utils.get(ctx.guild.text_channels, name=events_name)
        messages = await channel.history(limit=200).flatten()
        now = datetime.datetime.strptime(datetime.datetime.today().strftime(data_type), data_type)
        for message in messages:
            for emb in message.embeds:
                date, time, full = emb.description.split('\n', maxsplit=2)
                tail, date = date.split(' ', maxsplit=1)
                date, mon = date.split(' ', maxsplit=1)
                key_list = list(month_dict.keys())
                val_list = list(month_dict.values())
                #mon = key_list[val_list.index(mon)]
                tail, time, tail2 = time.split(' ', maxsplit=2)
                time = datetime.datetime.strptime(date + ' ' + mon + time, data_type)
                print(time)
                if now > time:
                    await message.delete()

    @commands.command(name="clear_events")
    async def clear_events(self, ctx):
        error_color = '#e02b2b'
        channel = utils.get(ctx.guild.text_channels, name=events_name)
        messages = await channel.history(limit=200).flatten()
        pprint(messages)
        for message in reversed(messages):
            if not message.author.bot:
                await message.delete()
            for emb in message.embeds:
                if str(emb.color) == error_color:
                    await message.delete()


    @commands.command(name="update_schedule")
    async def update_schedule(self, ctx, add_event=False):
        try:
            channel = utils.get(ctx.guild.text_channels, name=schedule_name)
            messages = await channel.history(limit=200).flatten()
            for message in messages:
                await message.delete()
            if not add_event:
                await News.clear_events(self, ctx)
            imageURL = 'https://cdn.discordapp.com/attachments/810929046329491456/862404560777904198/987d1c7da78b74d9.png'
            channel = utils.get(ctx.guild.text_channels, name=events_name)
            messages = await channel.history(limit=200).flatten()
            embed = Embed(
                title='Ближайшие события',
                color=config["info"]
            )
            for message in reversed(messages):
                description = ''
                for emb in message.embeds:
                    date, time, short, full = emb.description.split('\n', maxsplit=3)
                    tail, date = date.split(' ', maxsplit=1)
                    date, mon = date.split(' ', maxsplit=1)
                    tail, time, tail2 = time.split(' ', maxsplit=2)
                    time = datetime.datetime.strptime(date + ' ' + mon + time, data_type)
                    weekday = time.strftime('%A')
                    description += '[' + emb.title + '](https://discordapp.com/channels/' + str(ctx.guild.id) + '/' \
                                   + str(channel.id) + '/' + str(message.id) + ')'
                    embed.add_field(
                        name=f"\u200b",
                        value=f":pushpin: {description} — {date} {mon} ({weekday})",
                        inline=False
                    )
            embed.set_image(url=imageURL)
        except:
            embed = Embed(
                title='Ошибка чтения новостей',
                description='Удалите сообщения в событиях созданные вручную и добавьте ивенты через #add_event',
                color=config["error"]
            )
        if add_event:
            channel = utils.get(ctx.guild.text_channels, name=schedule_name)
            await channel.send(embed=embed)
        else:
            await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(News(bot))
