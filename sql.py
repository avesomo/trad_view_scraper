import psycopg2
from config import config
import numpy as np


def db_exists(db_name):
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(f"select exists(select * from information_schema.tables where table_name='{db_name}')")
        return cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_db(db_name):
    commands = [f"""
        CREATE TABLE {db_name} (
            id SERIAL PRIMARY KEY,
            open_time TIMESTAMP NOT NULL,
            open_price FLOAT NOT NULL,
            high_price FLOAT NOT NULL,
            low_price FLOAT NOT NULL,
            close_price FLOAT NOT NULL,
            volume FLOAT NOT NULL,
            close_time TIMESTAMP NOT NULL,
            quote FLOAT NOT NULL,
            no_trades INTEGER NOT NULL,
            taker_base FLOAT NOT NULL,
            taker_quote FLOAT NOT NULL,
            ignore_val INTEGER NOT NULL,
            ema12 FLOAT,
            ema26 FLOAT,
            ema50 FLOAT,
            ema200 FLOAT,
            short_gmma FLOAT,
            long_gmma FLOAT,
            d_gmmas FLOAT,   
            senkou_a FLOAT,
            senkou_b FLOAT,
            d_senkou FLOAT,
            macd FLOAT,
            rsi FLOAT,
            local_cloud FLOAT
        )"""]
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_markets_databases(markets, interval=('4H', )):
    for ti in interval:
        for market in markets:
            db_name = f'{market}_{ti}'.lower()
            if not db_exists(db_name):
                create_db(db_name)
                print(f"Database for {db_name} has been created.")
            else:
                print(f"Database {db_name} already exists.")


def insert_klines(klines, db_name, indicators):
    # todo - add only if such a kline doesnt exist - check the 'latest
    # todo - row' and compare it to current_time
    conn = None
    transformed = [i.get_attributes() for i in klines]
    values = np.c_[transformed[-len(indicators):], indicators]
    print(f'vals: {values}')
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(f"Select * FROM {db_name} LIMIT 0")
        columns = ', '.join([desc[0] for desc in cur.description][1:])
        print(f'Inserting klines data into sql table {db_name.upper()}...')
        for val in values:
            sql = f"""INSERT INTO %s (%s) VALUES %s""" % (db_name, columns, tuple(val))
            cur.execute(sql)
            conn.commit()
        print(f'{db_name.upper()} table data has been updated.\n')
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def get_klines_from_sql(db_name):
    # todo - add only if such a kline doesnt exist - check the 'latest
    # todo - row' and compare it to current_time
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(f"Select * FROM {db_name} LIMIT 0")
        columns = ', '.join([desc[0] for desc in cur.description][1:])
        cur.execute(f"SELECT {columns} FROM {db_name} ORDER BY open_time ASC")
        rows = cur.fetchall()
        print("The number of rows fetched: ", cur.rowcount)
        for row in rows:
            print(type(row), row)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
