# -*- coding: utf-8 -*-
import socket

import SQL_db
from SQL_db import get_one_string


def connect_laurent(name,ip,port,password):
    global sock_laurent
    sock_laurent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_laurent.settimeout(3)
    try:
        sock_laurent.connect((ip, port))
    except:
        print(f'Ошибка подключения к Laurent {name}')
        return False
    print(f'Подключение к реле {name} успешно')
    sock_laurent.sendall('$KE\r\n'.encode('utf-8'))
    data_byte = sock_laurent.recv(1024)
    data_byte = data_byte.decode('utf-8')
    if data_byte == "#OK\r\n":
        temp = '$KE,PSW,SET,' + password + '\r\n'
        sock_laurent.sendall(temp.encode('utf-8'))
        data_byte = sock_laurent.recv(1024)
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

def rig_reset(relay,time):
    temp = f'$KE,REL,{relay},{time}\r\n'.encode('utf-8')
    sock_laurent.sendall(temp)
    data_bytes = sock_laurent.recv(1024)

def miner_error_scan(miner_error):
    rig_with_error = []
    for i in miner_error.number:
        temp = SQL_db.get_one_string(i)

        rig_with_error.append(temp)
    print(rig_with_error)


