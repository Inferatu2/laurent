# -*- coding: utf-8 -*-
import socket
import os
import datetime
import threading
import SQL_db
import DB_SQL
import laurent
from config import conf_to_dict
from miner import Miner
from laurent import connect_laurent


class Miner_error:

    def __init__(self,miner_count):
        self.number = list()
        self.enabled = list()
        self.time_stop = list()
        self.time_offline = list()
        self.reboot_count = list()
        self.error = list()
        self.rig_with_error = list()
        for i in miner_count:
            self.number.append(i[0])
            self.enabled.append(False)
            self.time_stop.append(datetime.datetime.now())
            self.time_offline.append(None)
            self.reboot_count.append(0)
            self.error.append('')

    def setup_online(self, n):
        number = self.number.index(n)
        self.enabled[number] = True
        self.time_stop[number] = datetime.datetime.now()
        self.time_offline[number] = 0
        self.error = 'no'

    def setup_offline(self,n):
        number = self.number.index(n)
        self.enabled[number] = False
        self.time_offline[number] = datetime.datetime.now() - self.time_stop[number]
        print(f'майнер оффлайн {self.time_offline[number]}\n', end='')

# def laurent_start(number,laurent_numbe,relay):
#     locker = threading.RLock()
#     locker.acquire()
#     miner_error.setup_offline(number)
#     laurent_data = SQL_db.get_laurent_data(laurent_numbe, file_path_db)
#     if laurent_data == None:
#         print(f'реле {laurent_numbe} отсутствует в базе')
#         return
#     if connect_laurent(*laurent_data[1:5]):
#         print(f'подключились к реле {laurent_numbe} - {relay}')
#         laurent.rig_reset(relay, 0.5)
#     locker.release()



def scan_miners(result):
    locker = threading.RLock()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(int(configuration['miner_connect_time_out']))
    locker.acquire()
    miner = Miner(result)
    miner.connect(s)
    if miner.err:
        print(f'Ошибка подключения к майнеру {miner.name}\n',end='')
        miner_error.setup_offline(miner.number)
        # laurent_start(miner.number,miner.laurent,miner.relay)
        # обращаемся к реле еще одним потоком
        return
    miner.get_start(s)
    if miner.err:
        return
    miner.api_to_class()  # распарсим список и сохраняем в атрибуты класса
    miner.print()      # выводим результат
    miner_error.setup_online(miner.number)
    miner.proverka()
    locker.release()

def threed_regulator(miner_list, n=int):
    stop_thr = 0
    for rig in miner_list:
        stop_thr += 1
        result = SQL_db.get_one_string(rig[0])
        thr = threading.Thread(target=scan_miners, args=(result,),name=rig[0])
        thr.start()
        if stop_thr == int(n):
            thr.join()
            print(f"======== Цикл из {n} подключений прошел ==========")
            stop_thr = 0
    thr.join()
    print('\n========Сканирование завершено===========')
    laurent.miner_error_scan(miner_error)


def main():
    global configuration
    global miner_error
    global s
    global file_path_db

    file_path = str(os.getcwd())
    file_path_conf = os.path.join(file_path, "config.txt")
    configuration = conf_to_dict(file_path_conf)

    file_path = os.path.join(file_path, 'miner')
    file_path_db = os.path.join(file_path, 'mine_conf.db')
    if SQL_db.SQL_connect(file_path_db):
        print('ПОдключились к базе данных')
        main_scan_work = True # False если есть ошибка подключения к базе, не даст продолжить
        miner_count = SQL_db.get_miner_list()
        miner_error = Miner_error(miner_count)
        threed_regulator(miner_count, configuration['connect_at_moment'])
    else:
        print('ошибка подключения к базе данных')
        main_scan_work = False
        result = ''
        miner_count = 0


if __name__ == '__main__':
    main()


