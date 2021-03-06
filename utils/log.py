import logging
import traceback
from utils import sql

#logfile = config.log
log = logging.getLogger("my_log")
log.setLevel(logging.INFO)
#FH = logging.FileHandler(logfile, encoding='utf-8')
str_logging_format = "%(asctime)s-%(levelname)s-%(message)s"
log_format = '%(asctime)s : [%(levelname)s] : %(message)s'
basic_formater = logging.Formatter(log_format)
#FH.setFormatter(basic_formater)
#log.addHandler(FH)


def log_init():
    return log


def error(ctx, error_message: str):
    guild, guild_id = get_guild(ctx)
    message = f"Error {ctx.command} in {guild} " \
              f"by {ctx.message.author} (ID: {ctx.message.author.id})"
    print(message)
    log.error(str(error_message) + message)
    sql.error_log(ctx=ctx, error=error_message)


## функция для записи в лог сообщений об ошибке
def error_log(line_no):
    ## задаем формат ошибочных сообщений, добавляем номер строки
    err_formater = logging.Formatter('%(asctime)s : [%(levelname)s][LINE ' + line_no + '] : %(message)s')
    ## устанавливаем формат ошибок в логгер
    #FH.setFormatter(err_formater)
    #log.addHandler(FH)
    ## пишем сообщение error
    log.error(traceback.format_exc())
    ## возвращаем базовый формат сообщений
    #FH.setFormatter(basic_formater)
    #log.addHandler(FH)


def get_guild(ctx):
    if ctx.guild is None:
        guild = ''
        guild_id = ''
    else:
        try:
            guild = ctx.guild.name
            guild_id = ctx.message.guild.id
        except:
            guild = ctx.guild
            guild_id = ctx.guild_id
    return guild, guild_id


def get_author(ctx, slash=False):
    if slash:
        author = ctx.author
        author_id = ctx.author_id
    else:
        author = ctx.message.author
        author_id = ctx.author.id
    return author, author_id


def get_message(slash=False):
    if slash:
        return "Executed Slash Command"
    else:
        return "Executed"
