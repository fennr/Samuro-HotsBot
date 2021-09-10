""""
Основной файл бота
"""

import json
import os
import platform
import random
import sys

import discord
import yaml
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext  # Importing the newly installed library.

from helpers import sql, log
from scripts import heroes_ru_names

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

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)
slash = SlashCommand(bot, sync_commands=True)

sql.sql_init()

log = log.log_init()

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
    if ctx.guild is None:
        guild_name = ''
        guild_id = ''
    else:
        guild_name = ctx.guild.name
        guild_id = ctx.message.guild.id
    message = f"Executed {executedCommand} command in {guild_name} (ID: {guild_id}) " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    print(message)  # {ctx.guild.name} {ctx.message.guild.id}
    log.info(message)
    sql.info_log(ctx, executedCommand)

@bot.event
async def on_slash_command(ctx: SlashContext):
    executedCommand = ctx.name
    message = f"Executed {executedCommand} command in {ctx.guild} (ID: {ctx.guild_id}) " \
             f"by {ctx.author} (ID: {ctx.author_id})"
    print(message)
    log.info(message)
    sql.info_log(ctx, executedCommand)


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
    elif isinstance(error, commands.CommandInvokeError):
        text = "Ошибка! Герой не найден"
        embed = discord.Embed(
            title=text,
            color=config["error"]
        )
        embed.set_footer(
            text=f"Информация для: {ctx.author}"
        )
        await ctx.send(embed=embed)
    if ctx.guild is None:
        guild_name = ''
        guild_id = ''
    else:
        guild_name = ctx.guild.name
        guild_id = ctx.message.guild.id
    message = f" in {guild_name} " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    log.error(str(error) + message)
    sql.error_log(ctx=ctx, error=error)
    raise error

# Запрет писать боту в личку
@bot.check
async def global_guild_only(ctx):
    if ctx.message.author.id not in config["owners"]:
        if not ctx.guild:
            await ctx.send('Личка бота закрыта, пожалуйста используйте бота на сервере\n'
                           'Если по каким-то причинам неудобно использовать на публичном сервере всегда можно пригласить в свой по команде #invite')
            raise commands.NoPrivateMessage  # replicating guild_only check: https://github.com/Rapptz/discord.py/blob/42a538edda79f92a26afe0ac902b45c1ea20154d/discord/ext/commands/core.py#L1832-L1846
    return True

# Генерируем файл с именами героев
heroes_ru_names.create_heroes_ru_data()
# Run the bot with the token

bot.run(TOKEN)
