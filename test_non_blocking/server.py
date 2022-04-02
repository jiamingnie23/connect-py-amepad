# -*- coding: UTF-8 -*-
import socket
import select

sock = socket.socket()
sock.bind(('localhost', 8000))
sock.setblocking(False)
sock.listen(1)


inputs = [sock, ]

while True:
    r_list, w_list, e_list = select.select(inputs, [], [], 1)
    for event in r_list:
        if event == sock:
            print("新的客户端连接")
            new_sock, addr = event.accept()
            inputs.append(new_sock)
        else:
            data = event.recv(1024)
            if data:
                print("接收到客户端信息")
                print(data)
                event.sendall("test_response")
                event.close()
            else:
                print("客户端断开连接")
                inputs.remove(event)