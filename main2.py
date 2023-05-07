# -*- coding: utf-8 -*-

import time
import DB_SQL
import os
import threading
from config import conf_to_dict
from miner import Miner


def scan_miner(result, miner_count_number):
    miner = Miner(result)
    miner.err = "random text because first 'if miner.err' must be True"
    while True:
        if miner.err:
            miner.connect(int(configuration['miner_connect_time_out']))
        if miner.err:
            print(f'miner {miner.name} не в сети\n', end='')
            miners_status[miner_count_number] = miner
            time.sleep(int(configuration['scan_time']))
            continue
            # тут надо запустиь процесс перезагрузки
        miner.get_start()
        if miner.err:
            print(f'miner {miner.name} не в сети\n', end='')
            miners_status[miner_count_number] = miner
            time.sleep(int(configuration['scan_time']))
            continue
            # ребутаем
        print('Пoдключен ' + miner.name + '\n', end='')
        miner.api_to_class()  # распарсим список и сохраняем в атрибуты класса
        miner.print()  # выводим результат
        miners_status[miner_count_number] = miner
        time.sleep(int(configuration['scan_time']))


def all_miner_print():
    middle_temp_list = []
    while True:
        with threading.Lock():
            print('=============печатаем сведеную таблицу==============')
            print(f"имя        аптайм     хешрейд              шары    битшары   карты")
            for rig in miners_status:
                if rig:
                    if rig.err:
                        print(f'=========  {rig.name} offline  ==========')
                    else:
                        print(
                            f"{rig.name:<10} {rig.timeup:<10} {rig.obhash:<20} {rig.valid_share:<7} {rig.rez_share:<9}"
                            f"{rig.card_count:<5}")
            #         middle_temp_list.append(sum(rig.templist)/rig.card_count)
            # middle_temp = sum(middle_temp_list)//len(middle_temp_list)

        time.sleep(15)


def main():
    global configuration
    global file_path_db
    global miners_status
    miners_status = []
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
        miner_count_number = -1
        for miner in miner_list:
            miner_count_number = miner_count_number + 1
            miners_status.append('')
            result = data_base.get_one_miner(miner[0])
            thr = threading.Thread(target=scan_miner, args=(result, miner_count_number), name=miner[0])
            thr.start()
        threading.Timer(10, all_miner_print).start()


if __name__ == '__main__':
    main()
