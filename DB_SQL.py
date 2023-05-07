import sqlite3

class Db:
    def __init__(self,path):
        '''connect db'''
        try:
            self.conn = sqlite3.connect(path)
            self.cursor = self.conn.cursor()
            self.cursor_laurent = self.conn.cursor()
            self.enable = True
        except sqlite3.OperationalError:
            print('ошибка подключения к базе данных')
            self.enable = False

    def get_miner_list(self):
        '''get miner list from miner table'''
        self.cursor.execute(f"""SELECT №,IP,port FROM miner WHERE scan = 'yes';""")
        return self.cursor.fetchall()

    def get_one_miner(self,n):
        '''get all default parameters from miner table'''
        self.cursor.execute(f"SELECT * FROM miner WHERE № = ?;", (n,))
        return self.cursor.fetchone()

    def get_laurent_data(self,n):
        '''get all default parameters from laurent table'''
        self.cursor_laurent.execute(f"SELECT * FROM laurent WHERE № = {n};")
        return self.cursor_laurent.fetchone()