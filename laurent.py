# -*- coding: utf-8 -*-
import socket
from datetime import datetime
import time


class Laurent():
    def __init__(self,args):
        print(args)
        self.number, self.name, self.ip, self.port, self.password = args
        self.number_attempt_reset = 0

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

    def rig_reset(self, time):
        temp = f'$KE,REL,{relay},1,{time}\r\n'.encode('utf-8')
        self.sock_laurent.sendall(temp)
        data_bytes = self.sock_laurent.recv(1024)
        print(data_bytes)

    def rig_scan(self,miner, laurent_time_scan):
        if not miner.online:
            if miner.number_attempt_reset == 0:
                self.rig_reset(1)
                miner.laurent_await = True
            if miner.number_attempt_reset == 1:
                self.rig_reset(1)
                miner.laurent_await = True
            if miner.number_attempt_reset == 2:
                self.rig_reset(5)
                miner.laurent_await = True
            if miner.number_attempt_reset == 3:
                self.rig_reset(1)
                miner.laurent_await = True
            number_attempt_reset = number_attempt_reset + 1
            time.sleep(laurent_time_scan)
        miner.number_attempt_reset = miner.number_attempt_reset + 1
        miner.laurent_await = False
