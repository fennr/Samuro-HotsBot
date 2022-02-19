""""
Основной файл бота
"""

import json
import os
import platform
import random
import sys
import exceptions

import discord
import yaml
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext  # Importing the newly installed library.

from helpers import sql
from helpers.log import get_guild, log_init, error_log
from scripts import heroes_ru_names, google_table

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

GITHUB_TOKEN = os.environ.get('github_token')

if config['state'] == 'prod':
    TOKEN = os.environ.get('token_prod')
    APP_ID = os.environ.get('app_id_prod')
else:
    TOKEN = config['token_test']
    APP_ID = config['app_test']
    os.environ['TZ'] = 'Europe/Moscow'

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

bot = Bot(command_prefix=config["bot_prefix"], intents=intents, case_insensitive=True)
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
    with open("blacklist.json") as file:
        blacklist = json.load(file)
    with open("command_blacklist.json") as file:
        command_bl = json.load(file)
    if message.author.id in blacklist["ids"]:
        print(f"banned {message.author}")
        return
    if message.author.id in config["blacklist"]:
        print(f"banned {message.author}")
        return
    for bad_commands in command_bl:
        if bad_commands in message.context:
            print(f"Команда {bad_commands} в черном списке")
            return
    await bot.process_commands(message)


# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
    command_name = ctx.command.qualified_name
    command_args = ctx.command.signature
    command_string = f" {ctx.command.qualified_name} {ctx.command.signature}"
    guild, guild_id = get_guild(ctx)
    message = f"Executed {command_name} {command_args} command in {guild} (ID: {guild_id}) " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    print(message)  # {ctx.guild.name} {ctx.message.guild.id}
    log.info(message)
    sql.info_log(ctx, command_string[:20])


@bot.event
async def on_slash_command(ctx: SlashContext):
    executedCommand = ctx.name
    guild, guild_id = get_guild(ctx)
    message = f"Executed {executedCommand} command in {guild} (ID: {guild_id}) " \
              f"by {ctx.author} (ID: {ctx.author_id})"
    print(message)
    log.info(message)
    sql.info_log(ctx, executedCommand, slash=True)


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(ctx, error):
    print("Общая обработка ошибок")
    print(error)
    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return
    if isinstance(error, exceptions.UserNotAdmin):
        await ctx.send(exceptions.UserNotAdmin)
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
        '''elif isinstance(error, commands.CommandInvokeError):
        text = "Ошибка! Герой не найден"
        embed = discord.Embed(
            title=text,
            color=config["error"]
        )
        await ctx.send(embed=embed)'''
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Ошибка! Такой команды не существует",
            description=f"Воспользуйтесь справкой по команде {config['bot_prefix']}help",
            color=config["error"]
        )
        await ctx.send(embed=embed)
        embed.set_footer(
            text=f"Информация для: {ctx.author}"
        )
    log.error(ctx, error)
    sql.error_log(ctx, error)
    try:
        owner = ctx.get_member(int(config["owner"]))
        await owner.send(error)
    except:
        pass
    raise error

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
    message = f"Добро пожаловать на сервер **{member.guild.name}**.\n" \
              f"Располагайся по удобнее, не стесняйся использовать чат.\n" \
              f"Если захочется заходи в голосовые комнаты, все свои.\n\n" \
              f"Я один из ботов на сервере, отвечаю за ивенты, " \
              f"а так же могу предоставить много информации о талантах и билдах по **Heroes of the Storm**\n" \
              f"Чтобы посмотреть все мои доступные команды набери **#help**\n" \
              f"(желательно на отдельном канале для ботов)"
    embed = discord.Embed(
        title=title,
        description=message,
        color=config["success"]
    )
    message = f"На сервер '{member.guild.name}' " \
              f"пришел пользователь '{member.name}'"
    print(message)
    log.info(message)
    #sql.new_user_log(member, message)
    await member.send(embed=embed)


# Генерируем файл с именами героев
heroes_ru_names.create_heroes_ru_data()
# Генерируем данные из таблицы Сталка
# google_table.create_stlk_json()
# Run the bot with the token

bot.run(TOKEN)
