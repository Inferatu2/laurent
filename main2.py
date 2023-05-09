# -*- coding: utf-8 -*-

import os
import threading
import time
from datetime import datetime
import DB_SQL
import global_miner_scaner
from config import conf_to_dict
from laurent import Laurent
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
        with threading.RLock():
            global_miner_scaner.all_miner_check(miners_online, miners_offline, int(configuration['all_miner_result']))
        time.sleep(int(configuration['all_miner_result']))


def miner_offline(miner):
    miners_offline[miner.name] = miner
    miners_online.pop(miner.name, '')
    miner_time_off = datetime.now() - miner.time
    miner_time_off = miner_time_off.total_seconds() // 1
    time_from_last_reset = datetime.now() - miner.laurent_reset_time
    time_from_last_reset = time_from_last_reset.total_seconds() // 1
    if miner.reboot_bool:
        miner_start_relay(miner, time_from_last_reset)


def miner_start_relay(miner, time_from_last_reset):
    if time_from_last_reset > int(configuration['laurent_time_scan']):
        """miner_time_off это минуты от общего оффлайн времени майнера
        configuration['laurent_time_scan'] это через сколько надо ребутать риг. Подразумевается, что ндао
        подохдать, может он сам восстановится
        miner.laurent_await true если ребут был и мы выжидаем те самые configuration['laurent_time_scan']"""
        data_base = DB_SQL.Db(file_path_db)
        laurent_connect_data = data_base.get_laurent_data(miner.laurent)
        if laurent_connect_data is not None:  # get None if this row does not exist
            relay = Laurent(laurent_connect_data)
            data_base.close()
            print(f"{miner.name} ребутаем цикл {miner.number_attempt_reset} из ветки "
                  f"'rig {miner.name}, laurent {miner.laurent}, relay {miner.relay}'")
            # relay.start(miner)
            thr = threading.Thread(target=relay.start, args=(miner,),
                                   name=f'rig {miner.name}, laurent {miner.laurent}, relay {miner.relay}')
            thr.start()
        else:
            print(f'не существует реле {miner.laurent}')


def miner_online(miner):
    # print('Пoдключен ' + miner.name + '\n', end='')
    miner.json_to_class()  # распарсим список и сохраняем в атрибуты класса
    miner.print()  # выводим результат
    miner.time = datetime.now()
    miner.number_attempt_reset = 0
    miners_online[miner.name] = miner
    miners_offline.pop(miner.name, '')


def main():
    global configuration
    global file_path_db
    global miners_online
    global miners_offline

    miners_online = {}
    miners_offline = {}
    file_path = str(os.getcwd())
    file_path_conf = os.path.join(file_path, "config.txt")
    configuration = conf_to_dict(file_path_conf)

    file_path = os.path.join(file_path, 'miner')
    file_path_db = os.path.join(file_path, 'mine_conf.db')
    data_base = DB_SQL.Db(file_path_db)
    if data_base.enable:
        miner_list = data_base.get_miner_list()
        for miner in miner_list:
            result = data_base.get_one_miner(miner[0])  # miner[0] it's primary key of the miner
            thr = threading.Thread(target=scan_miner, args=(result,), name=miner[0])
            thr.start()
        data_base.close()
        threading.Timer(10, global_miner).start()


if __name__ == '__main__':
    main()
