import datetime
import threading
import time

def all_miner_print(miners_status, sleep_time):
        miners_status = [x for x in miners_status if x]
        print('=============печатаем сведеную таблицу===============')
        print(f"имя        аптайм     хешрейд              шары    битшары   карты")
        for rig in miners_status:
            if rig:
                if not rig.online:
                    print(f'{rig.name} offline  {datetime.datetime.now() - rig.time}')
                else:
                    print(
                        f"{rig.name:<10} {rig.timeup:<10} {rig.obhash:<20} {rig.valid_share:<7} {rig.rez_share:<9}"
                        f"{rig.card_count:<5}")
        all_miner_analise(miners_status)


def all_miner_analise(miners_status):
    middle_temp_list = []
    miners_status_online = [x for x in miners_status if x.online]
    for rig in miners_status_online:
        if rig.card_count:
            middle_temp_list.append(sum(map(int, rig.templist))/rig.card_count)  # middle temperage for this rig
    print(f'онлайн {len(miners_status_online)}')
    print(f'оффлайн {len(miners_status) - len(miners_status_online)}')
    if middle_temp_list:
        print(f'средняя температура карт {round(sum(middle_temp_list)/len(middle_temp_list))}')