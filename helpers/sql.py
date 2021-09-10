import psycopg2
import os
from datetime import datetime
import pytz


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
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        # close the communication with the database server by calling the close()
        if con is not None:
            con.close()
            # print('Database connection closed.')


def info_log(ctx, executedCommand):
    now = str(datetime.now(pytz.timezone('Europe/Moscow')))
    con = get_connect()
    cur = con.cursor()
    try:
        data = {'time': now[:25],
                'lvl': 'INFO',
                'command': executedCommand,
                'guild': str(ctx.guild.name)[:29],
                'guild_id': ctx.message.guild.id,
                'author': str(ctx.message.author)[:29],
                'author_id': ctx.message.author.id,
                'message': 'Executed'
                }
    except:
        data = {'time': now[:25],
                'lvl': 'INFO',
                'command': executedCommand,
                'guild': str(ctx.guild)[:29],
                'guild_id': ctx.guild_id,
                'author': str(ctx.author)[:29],
                'author_id': ctx.author_id,
                'message': 'Executed Slash Command'
                }
    cur.execute(
        '''INSERT INTO log(TIME, LVL, COMMAND, GUILD, GUILD_ID, AUTHOR, AUTHOR_ID, MESSAGE) 
        VALUES (%(time)s, %(lvl)s, %(command)s, %(guild)s, %(guild_id)s, %(author)s, %(author_id)s, %(message)s)''',
        data
    )
    con.commit()
    con.close()


def error_log(ctx, error):
    now = str(datetime.now(pytz.timezone('Europe/Moscow')))
    con = get_connect()
    cur = con.cursor()
    command = ' '.join(ctx.args[2:])  # первые два это системыне объекты hots object и Context object
    data = {'time': now[:25],
            'lvl': 'ERROR',
            'command': command[:19],
            'guild': str(ctx.guild.name)[:29],
            'guild_id': str(ctx.message.guild.id),
            'author': str(ctx.message.author)[:29],
            'author_id': str(ctx.message.author.id),
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
        return psycopg2.connect(dbname='discord', user='fenrir',
                                password='1121', host='localhost')
