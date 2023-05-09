import socket
import json
from datetime import datetime


class Miner:

    def __init__(self, result):
        """load default values from result for this miner
        result values example (4, 'miner2', 'yes', '127.0.0.1', 3334, 1, 18, 60, 0, 'yes', 2, 20, 'yes')
        self.scan_bool - do program need to scan this miner / надо ли вообще сканить этот майнер
        self.card_count_norm - default number of cards in rig / сколько должно быть карт в риге
        self.min_hash - minimum hashrate when the alarm is not triggered  / минимальный хешрейт
        self.max_temp - max card temperature / выбираем карту с макс температурой и сохраняем сюда
        self.max_rez_share - max regected shares when the alarm is not triggered /макс допустимое кол-во битых шар
        self.reboot_bool - must reboot in laurent  / ндао ли перезагружать риг с помощью лорент
        self.laurent - laurent number in table 'laurent' in SQLite /к какому лорент из табл 'laurent' привязан риг
        self.relay - relay numbe in laurent /номер реле у лорент
        self.message_bool - do program need to message about error of this miner /отправлять ли тревогу в телегу
        self.time - time, when this miner online last time / сохраняем туда время последнего онлайна
        self.laurent_await - if laurent try reboot and wait result, if true - dont try reboot one's more
        self.err - save error in this value / тут всякие ошибки храним
        """
        self.number, self.name, self.scan_bool, self.ip, self.port, self.card_count_norm, self.min_hash, self.max_temp, \
            self.max_rez_share, self.reboot_bool, self.laurent, self.relay, self.message_bool = result

        self.scan_bool = True if self.scan_bool.lower() == 'yes' else False
        self.reboot_bool = True if self.reboot_bool.lower() == 'yes' else False
        self.message_bool = True if self.message_bool.lower() == 'yes' else False
        self.time = datetime.now()
        self.online = False
        self.laurent_await = False
        self.number_attempt_reset = 0
        self.err = ''
        self.timeup = 0
        self.obhash = 0
        self.valid_share = 0
        self.rez_share = 0  # regected shares
        self.hashlist = list()  # list hashrates of card
        self.templist = list()  # temperature list of card
        self.kullist = list()
        self.pool = ''

    def connect(self, timeout):
        """connect for this miner"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
        try:
            self.s.connect((self.ip, self.port))
        except:
            # print('ошибка подключения ' + self.name +'\n',end='')
            self.online = False
        else:
            self.online = True

    def get_start(self):
        """sending a standard request get_start1
        waiting json answer
        example {"id":0,"jsonrpc":"2.0","result":["PM 6.2c - ETC", "5", "20966;0;0", "20966", "0;0;0", ' \
                           '"off", "73;52", "europe.etchash-hub.miningpoolhub.com:20615", "0;1;0;0"]}\n"""

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
            self.api_result = list(self.api_result['result'])  # в json ответе нам интересен только result, там список
            self.err = ''

    def json_to_class(self):
        '''parsing the json response into class attributes'''
        self.timeup = int(self.api_result[1])  # timeup of miner
        self.obhash = float(int(self.api_result[2].split(';')[0]) / 1000)  # result hashrate, changing to MH/s
        self.valid_share = int(self.api_result[2].split(';')[1])  # validshare
        self.rez_share = int(self.api_result[2].split(';')[2])  # regected shares
        self.hashlist = self.api_result[3].split(';')  # list hashrates of card

        for i, temp in enumerate(self.api_result[6].split(';')):
            if i % 2 == 0:
                self.templist.append(int(temp)) # only even values are the temperature of the cards
            else:
                self.kullist.append(int(temp))
        self.card_count = len(self.templist)
        self.pool = self.api_result[7]

    def print(self):
        '''display the data'''

        def list_to_str(mlist, razd='|'):
            return f'{razd}'.join(map(str, mlist))

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
        """we compare the reference value with the real one, if necessary, we trigger an alarm,
        if the reference value is set to zero, it means that this parameter does not need to be checked
        сравниваем эталонное значение с реальным, в случае необходимости запускаем тревогу,
        если эталонное значение установлено ноль, то это означает что данный параметр проверять не надо"""
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
