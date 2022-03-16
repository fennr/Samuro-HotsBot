import psycopg2
import psycopg2.extras
import os
from datetime import datetime
import pytz
from helpers import log


def sql_init():
    con = None
    # DATABASE_URL = os.environ.get('DATABASE_URL')
    try:
        # create a new database connection by calling the connect() function
        con = get_connect()

    except Exception as error:
        print('Cause: {}'.format(error))

    finally:
        #  create a new cursor
        cur = con.cursor()

        # execute an SQL statement to get the HerokuPostgres database version
        #print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        #print(db_version)
        # close the communication with the database server by calling the close()
        if con is not None:
            con.close()
            # print('Database connection closed.')


def new_user_log(member, message):
    now = str(datetime.now(pytz.timezone('Europe/Moscow')))
    con = get_connect()
    cur = con.cursor()
    data = {'time': now[:25],
            'lvl': 'INFO',
            'command': "new_user",
            'guild': str(member.guild.name)[:29],
            'guild_id': member.guild.id,
            'author': str(member.name)[:29],
            'author_id': member.id,
            'message': message
            }
    cur.execute(
        '''INSERT INTO new_users(TIME, LVL, COMMAND, GUILD, GUILD_ID, AUTHOR, AUTHOR_ID, MESSAGE) 
        VALUES (%(time)s, %(lvl)s, %(command)s, %(guild)s, %(guild_id)s, %(author)s, %(author_id)s, %(message)s)''',
        data
    )
    con.commit()
    con.close()


def info_log(ctx, executedCommand, slash=False):
    now = str(datetime.now(pytz.timezone('Europe/Moscow')))
    con = get_connect()
    cur = con.cursor()
    guild, guild_id = log.get_guild(ctx)
    author, author_id = log.get_author(ctx, slash)
    message = f"{log.get_message(slash)} : {executedCommand}"
    data = {'time': now[:25],
            'lvl': 'DONE',
            'command': executedCommand,
            'guild': str(guild)[:29],
            'guild_id': guild_id,
            'author': str(author)[:29],
            'author_id': author_id,
            'message': message[:149]
            }
    cur.execute(
        '''INSERT INTO "log"(TIME, LVL, COMMAND, GUILD, GUILD_ID, AUTHOR, AUTHOR_ID, MESSAGE) 
        VALUES (%(time)s, %(lvl)s, %(command)s, %(guild)s, %(guild_id)s, %(author)s, %(author_id)s, %(message)s)''',
        data
    )
    con.commit()
    con.close()


def error_log(ctx, error, slash=False):
    now = str(datetime.now(pytz.timezone('Europe/Moscow')))
    con = get_connect()
    cur = con.cursor()
    command = str(ctx.command)
    for item in ctx.args:
        if isinstance(item, str):
            command += ' ' + item
    guild, guild_id = log.get_guild(ctx)
    author, author_id = log.get_author(ctx, slash)
    data = {'time': now[:25],
            'lvl': 'ERROR',
            'command': command[:19],
            'guild': str(guild)[:29],
            'guild_id': str(guild_id),
            'author': str(author)[:29],
            'author_id': str(author_id),
            'message': str(error)[:149]
            }
    cur.execute(
        '''INSERT INTO log(TIME, LVL, COMMAND, GUILD, GUILD_ID, AUTHOR, AUTHOR_ID, MESSAGE) 
        VALUES (%(time)s, %(lvl)s, %(command)s, %(guild)s, %(guild_id)s, %(author)s, %(author_id)s, %(message)s)''',
        data
    )
    con.commit()
    con.close()


def get_connect():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        return psycopg2.connect(DATABASE_URL)
    except:
        return psycopg2.connect(dbname='postgres', user='postgres',
                                password='1121', host='localhost')

def get_cursor(con):
    return con.cursor(cursor_factory=psycopg2.extras.DictCursor)
