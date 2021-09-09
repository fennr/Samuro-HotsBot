import psycopg2
import datetime


if __name__ == '__main__':
    con = psycopg2.connect(dbname='discord', user='fenrir',
                           password='1121', host='localhost')
    cur = con.cursor()
    cur.execute(
        '''SELECT * FROM logs
            ORDER BY time DESC
            LIMIT 10
        '''
    )
    rec = cur.fetchall()
    log_name = 'main_log.log'
    with open(file=log_name, mode='w', encoding='utf-8') as log_file:
        log_file.write(rec)
    print(rec)
    con.commit()
    con.close()
    #records = cursor.fetchall()
    #print(records)
