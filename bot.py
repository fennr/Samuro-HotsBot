""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import json
import os
import platform
import random

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext  # Importing the newly installed library.

from utils.log import get_guild, log_init
from utils.classes import Const
from utils.classes.Const import config

# Вставить TOKEN и APP_ID вашего бота
if os.environ.get('TESTING'):
    TOKEN = os.environ.get('TOKEN')
    APP_ID = os.environ.get('APP_ID')
    os.environ['TZ'] = 'Europe/Moscow'
else:
    TOKEN = os.environ.get('token_prod')
    APP_ID = os.environ.get('app_id_prod')

intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix=config.bot_initial_prefix, intents=intents, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True)


# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print(f"Current version: {config.version}")
    print(f"Last update: {config.update}")
    print("-------------------")
    status_task.start()


# Setup the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = ["ARAM", f"{config.bot_prefix}help", "Storm League"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


# Удаление стандартного хелпа
bot.remove_command("help")

if __name__ == "__main__":
    # Загрузка всех cogs модулей
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


# Ивент срабатывающий при отправке любого сообщении, в том числе без префикса
@bot.event
async def on_message(message):
    # Игнорировать сообщения пользователей в блек листе
    if message.author.id in [*Const.black_list]:
        print(f"Блокировка команды от пользователя {message.author}")
        return
    # Игнорировать сообщения других ботов
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


# Событие срабатывает каждый раз, когда команда отработала *успешно*
@bot.event
async def on_command_completion(ctx):

    command_name = ctx.command.qualified_name
    content = ctx.message.content[1:20]
    guild, guild_id = get_guild(ctx)
    message = f"Executed '{ctx.message.content[1:]}' command in {guild} " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    print(message)  # {ctx.guild.name} {ctx.message.guild.id}


# Событие срабатывает каждый раз, когда слеш команда отработала *успешно*
@bot.event
async def on_slash_command(ctx: SlashContext):
    executedCommand = ctx.name
    guild, guild_id = get_guild(ctx)
    message = f"Executed {executedCommand} command in {guild} (ID: {guild_id}) " \
              f"by {ctx.author} (ID: {ctx.author_id})"
    print(message)


# Запрет писать боту в личку. Исключения: автор бота или команда help
@bot.check
async def global_guild_only(ctx):
    white_list = [
        'help',
    ]
    if ctx.message.author.id not in config.owners:
        if ctx.command.qualified_name not in white_list:
            if not ctx.guild:
                await ctx.send('Личка бота закрыта, пожалуйста используйте бота на сервере\n'
                               'Если по каким-то причинам неудобно использовать на публичном сервере нажмите на аватар и кликните по кнопке "Добавить на сервер"')
                raise commands.NoPrivateMessage  # replicating guild_only check: https://github.com/Rapptz/discord.py/blob/42a538edda79f92a26afe0ac902b45c1ea20154d/discord/ext/commands/core.py#L1832-L1846
    return True


# Приветствие при входе на сервер
'''@bot.event
async def on_member_join(member):
    server = member.guild
    title = "Привет друг!"
    message = f"Добро пожаловать на сервер **{member.guild.name}**.\n"
    embed = discord.Embed(
        title=title,
        description=message,
        color=config.success
    )
    message = f"На сервер '{member.guild.name}' " \
              f"пришел пользователь '{member.name}'"
    print(message)
    try:
        await member.send(embed=embed)
    except Exception:
        print(f"Невозможно отправить сообщение пользователю {member.name}")'''


# Генерируем файл с именами героев
#heroes_ru_names.create_heroes_ru_data()

# Run the bot with the token
bot.run(TOKEN)
