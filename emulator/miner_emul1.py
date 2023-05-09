# -*- coding: utf-8 -*-
import socket
import selectors

print('miner1 port 3333')
selector = selectors.DefaultSelector()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(('localhost',3333))
    server_socket.listen()
    selector.register(fileobj=server_socket, events=selectors.EVENT_READ, data=accept_connection)

def accept_connection(server_socket):
    client_socket, addr = server_socket.accept()
    print('Connection from', addr)
    selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=send_message)

def send_message(client_socket):
    try:
        request = client_socket.recv(1024)
    except:
        print('пока')
        request = ''
    if request == b'{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n':
        response = '{"id":0,"jsonrpc":"2.0","result":["PM 6.2c - ETC", "5", "20966;0;0", "20966", "0;0;0", ' \
                           '"off", "73;52", "europe.etchash-hub.miningpoolhub.com:20615", "0;1;0;0"]}\n'.encode()
        client_socket.sendall(response)
        print('miner1 <<' + str(request))
        print('miner1 >>' + str(response))
    else:
        selector.unregister(client_socket)
        print(f'miner1 << некорректный запрос {request}')
        client_socket.close()

def event_loop():
    while True:
        events = selector.select()

        for key, _ in events:
            callback = key.data
            callback(key.fileobj)

if __name__ == '__main__':
    server()
    event_loop()