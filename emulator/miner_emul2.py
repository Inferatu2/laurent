# -*- coding: utf-8 -*-
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
cur = server_socket.bind(('localhost',3334))
server_socket.listen()

print('miner2 port 3334')
while True:
    client_socket, addr = server_socket.accept()
    print('Connection from', addr)
    while True:
        request = client_socket.recv(1024)
        request = request.decode('utf-8')
        response = 'error'
        print(request)

        if not request:
            continue
        else:
            if request == '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n':
                response = '{"id":0,"jsonrpc":"2.0","result":["PM 6.2c - ETC", "25", "20966;0;200", "20966", "0;0;0", ' \
                           '"off", "73;52", "europe.etchash-hub.miningpoolhub.com:20615", "0;1;0;0"]}\n'

            client_socket.sendall(response.encode('utf-8'))
            print('miner2 >>' + response)