""""
Основной файл бота
"""

import json
import os
import platform
import random

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext  # Importing the newly installed library.

from utils import sql
from utils.library import files
from utils.log import get_guild, log_init

config = files.get_yaml("config.yaml")

if os.environ.get('TESTING'):
    TOKEN = os.environ.get('TOKEN')
    APP_ID = os.environ.get('APP_ID')
    os.environ['TZ'] = 'Europe/Moscow'
else:
    TOKEN = os.environ.get('token_prod')
    APP_ID = os.environ.get('app_id_prod')

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

bot = Bot(command_prefix=config["bot_initial_prefix"], intents=intents, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True)

sql.sql_init()

log = log_init()


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
    with open("data/blacklist.json") as file:
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
    command_name = ctx.command.qualified_name
    content = ctx.message.content[1:20]
    guild, guild_id = get_guild(ctx)
    message = f"Executed '{ctx.message.content[1:]}' command in {guild} " \
              f"by {ctx.message.author}"
    print(message)  # {ctx.guild.name} {ctx.message.guild.id}
    log.info(message)
    sql.info_log(ctx, command_name, content[:20])


@bot.event
async def on_slash_command(ctx: SlashContext):
    executedCommand = ctx.name
    guild, guild_id = get_guild(ctx)
    message = f"Executed {executedCommand} command in {guild} (ID: {guild_id}) " \
              f"by {ctx.author} (ID: {ctx.author_id})"
    print(message)
    log.info(message)
    #sql.info_log(ctx, executedCommand, slash=True)


# Запрет писать боту в личку
@bot.check
async def global_guild_only(ctx):
    white_list = [
        'help',
    ]
    if ctx.message.author.id not in config["owners"]:
        if ctx.command.qualified_name not in white_list:
            if not ctx.guild:
                await ctx.send('Личка бота закрыта, пожалуйста используйте бота на сервере\n'
                               'Если по каким-то причинам неудобно использовать на публичном сервере нажмите на аватар и кликните по кнопке "Добавить на сервер"')
                raise commands.NoPrivateMessage  # replicating guild_only check: https://github.com/Rapptz/discord.py/blob/42a538edda79f92a26afe0ac902b45c1ea20154d/discord/ext/commands/core.py#L1832-L1846
    return True


# Приветствие при входе на сервер
@bot.event
async def on_member_join(member):
    server = member.guild
    title = "Привет друг!"
    message = f"Добро пожаловать на сервер **{member.guild.name}**.\n"
    embed = discord.Embed(
        title=title,
        description=message,
        color=config["success"]
    )
    message = f"На сервер '{member.guild.name}' " \
              f"пришел пользователь '{member.name}'"
    print(message)
    log.info(message)
    # sql.new_user_log(member, message)
    try:
        await member.send(embed=embed)
    except:
        print(f"Невозможно отправить сообщение пользователю {member.name}")


# Генерируем файл с именами героев
#heroes_ru_names.create_heroes_ru_data()

# Run the bot with the token
bot.run(TOKEN)
