""""
Основной файл бота
"""

import json
import os
import platform
import random
import sys
import logging
import traceback
import datetime

import psycopg2

import discord
import yaml
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand  # Importing the newly installed library.

from scripts import heroes_ru_names

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

GITHUB_TOKEN = os.environ.get('github_token')

TOKEN = os.environ.get('token_prod')
APP_ID = os.environ.get('app_id_prod')

# read database connection url from the enivron variable we just set.
DATABASE_URL = os.environ.get('DATABASE_URL')
con = None
try:
    # create a new database connection by calling the connect() function
    con = psycopg2.connect(DATABASE_URL)

    #  create a new cursor
    cur = con.cursor()

    # execute an SQL statement to get the HerokuPostgres database version
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    print(db_version)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs(
          time CHAR(30) PRIMARY KEY,
          lvl  CHAR(10),
          message CHAR(150)
        );
    """)

    # close the communication with the HerokuPostgres
    cur.close()
except Exception as error:
    print('Cause: {}'.format(error))

finally:
    # close the communication with the database server by calling the close()
    if con is not None:
        con.close()
        print('Database connection closed.')
'''
TOKEN = config['token_test']
APP_ID = config['app_test']
con = None
try:
    con = psycopg2.connect(dbname='discord', user='fenrir',
                        password='1121', host='localhost')
    cursor = con.cursor()
    cursor.execute('SELECT * FROM public.products '
                   'ORDER BY id ASC')
    records = cursor.fetchall()
    print(records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs(
          time CHAR(30) PRIMARY KEY,
          lvl  CHAR(10),
          message CHAR(150)
        );
    """)

except Exception as error:
    print('Cause: {}'.format(error))
finally:
    # close the communication with the database server by calling the close()
    if con is not None:
        con.close()
        print('Database connection closed.')
'''

"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.emojis = True
intents.bans = True
intents.guild_typing = False
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.guild_messages = True
intents.guild_reactions = True
intents.integrations = True
intents.invites = True
intents.voice_states = False
intents.webhooks = False

Privileged Intents (Needs to be enabled on dev page), please use them only if you need them:
intents.presences = True
intents.members = True
"""


intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)
slash = SlashCommand(bot, sync_commands=True)

logfile = config["log"]
log = logging.getLogger("my_log")
log.setLevel(logging.INFO)
FH = logging.FileHandler(logfile, encoding='utf-8')
str_logging_format = "%(asctime)s-%(levelname)s-%(message)s"
log_format = '%(asctime)s : [%(levelname)s] : %(message)s'
basic_formater = logging.Formatter(log_format)
FH.setFormatter(basic_formater)
log.addHandler(FH)

## функция для записи в лог сообщений об ошибке
def error_log(line_no):
    ## задаем формат ошибочных сообщений, добавляем номер строки
    err_formater = logging.Formatter('%(asctime)s : [%(levelname)s][LINE ' + line_no + '] : %(message)s')
    ## устанавливаем формат ошибок в логгер
    FH.setFormatter(err_formater)
    log.addHandler(FH)
    ## пишем сообщение error
    log.error(traceback.format_exc())
    ## возвращаем базовый формат сообщений
    FH.setFormatter(basic_formater)
    log.addHandler(FH)

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    # print(f"All servers: {bot.guilds}")
    print("-------------------")
    status_task.start()


# Setup the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = ["ARAM", f"{config['bot_prefix']}help", "квикосы"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user
    with open("blacklist.json") as file:
        blacklist = json.load(file)
    if message.author.id in blacklist["ids"]:
        print(f"banned {message.author}")
        return
    if message.author.id in config["blacklist"]:
        print(f"banned {message.author}")
        return
    await bot.process_commands(message)


# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    # {ctx.channel.id} {ctx.message.id}
    # {ctx.guild.name} {ctx.message.guild.id}
    message = f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    print(message)  # {ctx.guild.name} {ctx.message.guild.id}
    log.info(message)
    now = str(datetime.datetime.now())
    #con = psycopg2.connect(dbname='discord', user='fenrir',
    #                       password='1121', host='localhost')
    con = psycopg2.connect(DATABASE_URL)
    cur = con.cursor()
    data = {'time': now, 'lvl': 'INFO', 'message': message}
    cur.execute(
        "INSERT INTO logs(TIME, LVL, MESSAGE) VALUES (%(time)s, %(lvl)s, %(message)s)", data
    )
    con.commit()
    con.close()


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Error!",
            description="This command is on a %.2fs cool down" % error.retry_after,
            color=config["error"]
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You are missing the permission `" + ", ".join(
                error.missing_perms) + "` to execute this command!",
            color=config["error"]
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Ошибка! Такой команды не существует",
            description=f"Воспользуйтесь справкой по команде {config['bot_prefix']}help",
            color=config["error"]
        )
        await ctx.send(embed=embed)
    message = f" in {ctx.guild.name} " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    log.error(str(error) + message)
    raise error

# Генерируем файл с именами героев
heroes_ru_names.create_heroes_ru_data()
# Run the bot with the token

bot.run(TOKEN)
