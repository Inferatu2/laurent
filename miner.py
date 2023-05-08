import socket
import json
from datetime import datetime

class Miner:

    def __init__(self, result):
        '''загружаем эталонные значения для майнера в атрибуты класса'''
        self.err = ''
        self.number, self.name, self.scan_bool, self.ip, self.port, self.card_count_norm, self.min_hash, \
        self.max_temp, self.max_rez_share, self.reboot_bool, self.laurent, self.relay, \
            self.message_bool = result

        self.scan_bool = True if self.scan_bool.lower() == 'yes' else False
        self.reboot_bool = True if self.reboot_bool.lower() == 'yes' else False
        self.message_bool = True if self.message_bool.lower() == 'yes' else False
            # загружаем порядковый номер майнера, его имя, надо ли его сканировать или оставить в покое,
            # айпишник, порт для api, сколько карт в нем должно быть, минимально допустимый хешрейд
            # максимально допустимую температуру, макс допустимое количество битых шар, надо ли ребутать автоматом
            # номер реле к которому привязан майнер и надо ли отправлять уведомление если майнер чудит
        # print('загрузили конфигурацию ' + self.name)
        self.time = datetime.now()
        self.online = False


    def connect(self,timeout):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
        '''устанавливаем соединение с манером'''
        try:
            self.s.connect((self.ip, self.port))
        except:
            # print('ошибка подключения ' + self.name +'\n',end='')
            self.online = False
        else:
            self.online = True

    def get_start(self):
        '''отправляем стандартный запрос майнеру, получаем ответ о состоянии'''

        params = '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'
        try:
            self.s.sendall(bytes(params + '\n', 'utf-8'))
            data_bytes = self.s.recv(1024)
            self.api_result = json.loads(data_bytes.decode('utf-8'))
        except json.decoder.JSONDecodeError as err:
            self.err = f'Ответ от майнера {self.name} некорректен'
        except (ConnectionAbortedError, ConnectionResetError) as err:
            self.err = f"Майнер {self.name} разорвал соединение"
            self.close()
        except socket.timeout as err:
            self.err = f"майнер {self.name} долго отвечает"
        except Exception as err:
            self.err = f"майнер {self.name} неизвестная ошибка {err}"
        else:
            self.api_result = list(self.api_result['result'])          # в json ответе нам интересен только result, там список
            self.err = ''

    def api_to_class(self):
        '''присваиваем полученные от майнера данные в атрибуты класса'''

        self.timeup = int(self.api_result[1])                              # аптайм майнера
        self.obhash = float(int(self.api_result[2].split(';')[0]) / 1000)    # общий хешрейд, из kH/s переводим в MH/s
        self.valid_share = int(self.api_result[2].split(';')[1])           # пойманые шары
        self.rez_share = int(self.api_result[2].split(';')[2])             # битые шары
        self.hashlist = self.api_result[3].split(';')                      # хешрейд карт отдельно
        self.templist = list()                          # температуры карт
        self.kullist = list()                           # скорость вентиляторов карт

        b = True  # все нечетные зн 6-го элемента с температурами в один список, все четные со скоростью кулера в другой
        j = 0
        for i in self.api_result[6].split(';'):
            if b:
                self.templist.append(int(i))
                b = False
                j += 1          # заодно считаем количество карт
            else:
                self.kullist.append(i)
                b = True
        del b
        self.card_count = j
        del j
        self.pool = self.api_result[7]

    def print(self):
        '''выводим данные на экран'''

        def list_to_str(mlist, razd='|'):
            return f'{razd}'.join(mlist)
        result = f"\tМайнер {self.name} работает {self.timeup} min, " \
                 f"карты {self.card_count} из {self.card_count_norm}," \
                 f" хешрейд карт {list_to_str(self.hashlist)} " \
                 f"общий хешрейд {self.obhash}Mh/s, " \
                 f"температуры {list_to_str(str(self.templist))}, " \
                 f"кулеры {list_to_str(self.kullist)}, " \
                 f"шар принято {self.valid_share}, " \
                 f"битых шар {self.rez_share}\n"
        print(result, end='')

    def check(self):
        '''сравниваем эталонное значение с реальным, в случае необходимости запускаем тревогу,
        если эталонное значение установлено ноль, то это означает что данный параметр проверять не надо'''

        temp = self.card_count_norm - self.card_count
        if temp > 0 and self.card_count_norm != 0:
            print(f"{self.name} вылетело {temp} карт")
        temp = self.rez_share - self.max_rez_share
        if temp > 0 and self.max_rez_share != 0:
            print(f"{self.name} битые шары превысили {self.max_rez_share} штук")
        temp = self.min_hash - int(self.obhash)
        if temp > 0 and self.min_hash != 0:
            print(f"{self.name} предупреждение, хешрейд ниже критичного на {temp} MH/s")
        temp = int(max(self.templist)) - self.max_temp
        if temp > 0 and self.max_temp != 0:
            print(f'{self.name} превышение температуры на {temp}')
        for i in range(len(self.hashlist)):
            if not int(self.hashlist[i]):
                print(f"{self.name} нулевой хешрейд {i} карты")

    def close(self):
        self.s.close()
        self.online = False