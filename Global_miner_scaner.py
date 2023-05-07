import threading
import time

def all_miner_print(miners_status):
    middle_temp_list = []
    with threading.Lock():
        print('=============печатаем сведеную таблицу===============')
        print(f"имя        аптайм     хешрейд              шары    битшары   карты")
        for rig in miners_status:
            if rig:
                if rig.err:
                    print(f'=========  {rig.name} offline  ==========')
                else:
                    print(
                        f"{rig.name:<10} {rig.timeup:<10} {rig.obhash:<20} {rig.valid_share:<7} {rig.rez_share:<9}"
                        f"{rig.card_count:<5}")
                middle_temp_list.append(sum(rig.templist)/rig.card_count)
            # middle_temp = sum(middle_temp_list)//len(middle_temp_list)



def all_miner_analise(miners_status):
    for rig in miners_status:
