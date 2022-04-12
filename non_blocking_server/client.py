import socket


def client_program():
    host = "localhost"  # as both code is running on same pc
    port = 8080  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = "getinfo"  # take input

    client_socket.send(message.encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response

    print('Received from server: ' + data)  # show in terminal

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()