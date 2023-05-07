import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
cur = server_socket.bind(('localhost',2424))
server_socket.listen()

print('Laurent')
while True:
    client_socket, addr = server_socket.accept()
    print('Connection from', addr)
    while True:
        request = client_socket.recv(1024)
        request = request.decode()
        response = 'error'
        print(request)

        if not request:
            break
        else:
            if request == "$KE\r\n":
                response = "#OK\r\n"
            elif request[0:12] == "$KE,PSW,SET,":
                response = "#PSW,SET,OK\r\n"
            elif request[0:8] == "$KE,REL,":
                response = "#REL,OK"
            client_socket.sendall(response.encode())
            print('>>' + response)