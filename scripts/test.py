import psycopg2
import datetime


if __name__ == '__main__':
    con = psycopg2.connect(dbname='discord', user='fenrir',
                           password='1121', host='localhost')
    cur = con.cursor()
    now = str(datetime.datetime.now())
    level = 'INFO'
    message = 'test message'
    data = {'time':now, 'lvl': level, 'message': message}
    cur.execute(
        "INSERT INTO logs(TIME, LVL, MESSAGE) VALUES (%(time)s, %(lvl)s, %(message)s)", data
    )
    con.commit()
    con.close()
    #records = cursor.fetchall()
    #print(records)
