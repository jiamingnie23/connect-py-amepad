#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   Date    :   17/2/25 上午11:13
#   Desc    :   测试 client

import socket

SERVER_ADDRESS = (HOST, PORT) = 'localhost', 8000 


def send_message(s, message):
    """
    发送请求
    """
    s.sendall(message)


def client():
    message = "Hello, I'm client"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    send_message(s, message)
    print('Client is Waiting response...')
    data = s.recv(1024)
    s.close()
    print('Client recv:', repr(data))  # 打印从服务器接收回来的数据

if __name__ == '__main__':
    client()