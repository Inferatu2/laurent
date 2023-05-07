import sqlite3

def SQL_connect(file_path):
    '''подключаемся к базе данных, курсор в глобальную переменную, в return булево значение как результат подключения'''
    try:
        global cur
        global conn
        conn = sqlite3.connect(file_path)
        cur = conn.cursor()
        return True
    except sqlite3.OperationalError:
        print('ошибка подключения к базе данных')
        return False

def get_miner_list():
    '''получить список номеров майнеров из таблицы'''
    cur.execute(f"""SELECT №,IP,port FROM miner;""")
    return cur.fetchall()

def get_one_string(n):
    '''получаем все параметры майнера из таблицы miner'''
    cur.execute(f"SELECT * FROM miner WHERE № = ?;", (n,))
    return cur.fetchone()

def get_laurent_data(n,file_path):

    conn2 = sqlite3.connect(file_path)
    cur2 = conn2.cursor()
    cur2.execute(f"SELECT * FROM laurent WHERE № = {n};")
    return cur2.fetchone()
