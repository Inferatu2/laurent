# -*- coding: utf-8 -*-

from datetime import datetime
import os
import threading
import time

import DB_SQL
import global_miner_scaner
from laurent import Laurent
from config import conf_to_dict
from miner import Miner


def scan_miner(result):
    """Мы не закрываем подключение по сокету между опросами, оно постоянно открыто и майнер постоянно опрашивается
    поэтому есть переменная miner.err, если она пустая, значит майнер подключен, надо только првоести опрос,
    если она хоть что-то содержит, значит была ошибка и надо пытаться подключиться.
    Функци miner.connect и miner.getstart обнуляют эту переменную или сохраняют туда исключение"""
    miner = Miner(result)
    while True:
        if not miner.online:
            miner.connect(int(configuration['miner_connect_time_out']))
        if not miner.online:
            miner_offline(miner)
            time.sleep(int(configuration['scan_time']))
            continue
            # тут надо запустиь процесс перезагрузки
        miner.get_start()
        if miner.err:
            miner_offline(miner)
            time.sleep(int(configuration['scan_time']))
            continue
            # ребутаем
        if not miner.err:
            miner_online(miner)
        time.sleep(int(configuration['scan_time']))


def global_miner():
    while True:
        with threading.Lock():
            global_miner_scaner.all_miner_check(miners_online, miners_offline, int(configuration['all_miner_result']))
        time.sleep(int(configuration['all_miner_result']))


def miner_offline(miner):
    miners_offline[miner.name] = miner
    miners_online.pop(miner.name, '')
    miner_time_off = str(datetime.now() - miner.time)
    print(f'майнер {miner.name} оффлайн {miner_time_off}\n', end='')
    miner_time_off = miner_time_off.split(':')[-1]
    miner_time_off = miner_time_off.split('.')[0] # строчка только для теста
    if not miner.laurent_await:
        miner_start_relay(miner, miner_time_off)


def miner_start_relay(miner, miner_time_off):
    if int(miner_time_off) > int(configuration['laurent_time_scan']) and not miner.laurent_await:
        data_base = DB_SQL.Db(file_path_db)
        laurent_connect_data = data_base.get_laurent_data(miner.laurent)
        if laurent_connect_data != None:
            relay = Laurent(laurent_connect_data)
            data_base.close()
            if relay.connect():
                if relay.login():
                    print(f'{miner.name} ребутаем цикл {miner.number_attempt_reset}')
                    thr = threading.Thread(target=relay.rig_scan, args=(miner, int(configuration['laurent_time_scan'])),
                                           name=f'rig {miner.name}, laurent {relay.name}, relay {miner.relay}')
                    miner.laurent_await = True
                    thr.start()
        else:
            print(f'не существует реле {miner.laurent}')

def miner_online(miner):
    print('Пoдключен ' + miner.name + '\n', end='')
    miner.api_to_class()  # распарсим список и сохраняем в атрибуты класса
    miner.print()  # выводим результат
    miner.time = datetime.datetime.now()
    miners_online[miner.name] = miner
    miners_offline.pop(miner.name, '')


def main():
    global configuration
    global file_path_db
    global miners_online
    global miners_offline
    laurent_list = []
    miners_online = {}
    miners_offline = {}
    main_scan_work = False
    file_path = str(os.getcwd())
    file_path_conf = os.path.join(file_path, "config.txt")
    configuration = conf_to_dict(file_path_conf)

    file_path = os.path.join(file_path, 'miner')
    file_path_db = os.path.join(file_path, 'mine_conf.db')
    data_base = DB_SQL.Db(file_path_db)
    if data_base.enable:
        print('Подключились к базе данных')
        main_scan_work = True  # False если есть ошибка подключения к базе, не даст продолжить
        miner_list = data_base.get_miner_list()
        for miner in miner_list:
            result = data_base.get_one_miner(miner[0])  # miner[0] it's name of the miner
            thr = threading.Thread(target=scan_miner, args=(result, ), name=miner[0])
            thr.start()
        laurent_list = data_base.get_laurent_list()
        data_base.close()
        threading.Timer(10, global_miner).start()


if __name__ == '__main__':
    main()
