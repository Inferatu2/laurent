# -*- coding: utf-8 -*-
from datetime import datetime
import socket


class Laurent:
    def __init__(self, args):
        self.number, self.name, self.ip, self.port, self.password = args
        self.number_attempt_reset = 0
        self.max_cycle = 4
        self.error = ""

    def connect(self):
        self.sock_laurent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_laurent.settimeout(3)
        try:
            self.sock_laurent.connect((self.ip, int(self.port)))
        except:
            print(f'Ошибка подключения к Laurent {self.name}')
            return False
        print(f'Подключение к реле {self.name} успешно')
        return True

    def login(self):
        self.sock_laurent.sendall('$KE\r\n'.encode('utf-8'))
        data_byte = self.sock_laurent.recv(1024)
        data_byte = data_byte.decode('utf-8')
        if data_byte == "#OK\r\n":
            temp = '$KE,PSW,SET,' + self.password + '\r\n'
            self.sock_laurent.sendall(temp.encode('utf-8'))
            data_byte = self.sock_laurent.recv(1024)
            data_byte = data_byte.decode('utf-8')
            if data_byte == "#PSW,SET,OK\r\n":
                print("Опрос реле проведен, пароль принят")
                return True
            else:
                print('реле не принимает пароль')
                return False
        else:
            print('реле не подтвердило соединение')
            return False

    def rig_reset(self, relay, time):
        temp = f'$KE,REL,{relay},1,{time}\r\n'.encode('utf-8')
        self.sock_laurent.sendall(temp)
        data_bytes = self.sock_laurent.recv(1024)
        if data_bytes[0:7] == b'#REL,OK':
            print(f'реле {relay} установлено на {time} сек')

    def rig_scan(self, miner):
        if not miner.online:
            if miner.number_attempt_reset == 0:
                self.rig_reset(miner.relay, 1)
            if miner.number_attempt_reset == 1:
                self.rig_reset(miner.relay, 1)
            if miner.number_attempt_reset == 2:
                self.rig_reset(miner.relay, 5)
            if miner.number_attempt_reset == 3:
                self.rig_reset(miner.relay, 1)
            if miner.number_attempt_reset > 3:
                print('кирдык ригу')
                return
            miner.laurent_reset_time = datetime.now()
            miner.number_attempt_reset = miner.number_attempt_reset + 1
        else:
            return

    def close(self):
        self.sock_laurent.close()

    def start(self, miner):
        if not miner.online:
            if self.connect():
                if self.login():
                    self.rig_scan(miner)
                self.close()
