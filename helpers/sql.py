import psycopg2
import os


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
            print('Database connection closed.')


def get_connect():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        return psycopg2.connect(DATABASE_URL)
    except:
        return psycopg2.connect(dbname='discord', user='fenrir',
                                password='1121', host='localhost')
