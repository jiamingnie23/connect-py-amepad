# import errno
# import os
# import signal
# import socket

# SERVER_ADDRESS = (HOST, PORT) = 'localhost', 8000
# REQUEST_QUEUE_SIZE = 1024


# def grim_reaper(signum, frame):
#     while True:
#         try:
#             pid, status = os.waitpid(
#                 -1,          # Wait for any child process
#                  os.WNOHANG  # Do not block and return EWOULDBLOCK error
#             )
#         except OSError:
#             return

#         if pid == 0:  # no more zombies
#             return


# def handle_request(client_connection):
#     request = client_connection.recv(1024)
#     print(request.decode())
#     http_response = b"""\
# HTTP/1.1 200 OK

# Hello, World!
# """
#     client_connection.sendall(http_response)


# def serve_forever():
#     listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     listen_socket.bind(SERVER_ADDRESS)
#     listen_socket.listen(REQUEST_QUEUE_SIZE)
#     print('Serving HTTP on port {port} ...'.format(port=PORT))

#     signal.signal(signal.SIGCHLD, grim_reaper)

#     while True:
#         try:
#             client_connection, client_address = listen_socket.accept()
#         except IOError as e:
#             code, msg = e.args
#             # restart 'accept' if it was interrupted
#             if code == errno.EINTR:
#                 continue
#             else:
#                 raise

#         pid = os.fork()
#         if pid == 0:  # child
#             listen_socket.close()  # close child copy
#             handle_request(client_connection)
#             client_connection.close()
#             os._exit(0)
#         else:  # parent
#             client_connection.close()  # close parent copy and loop over

# if __name__ == '__main__':
#     serve_forever()

import socket

import time

import threading

def handle_socket(conn, addr):
    while True:
        data = conn.recv(1024)

        print(data.decode('utf-8'))

        time.sleep(3)

        send_data = 'got it'

        conn.send(send_data.encode('utf-8'))

        conn.close()

if __name__ == '__main__':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(('0.0.0.0', 8000))

    s.listen()

    while True:
        conn, addr = s.accept()

        client_thread = threading.Thread(target=handle_socket, args=[conn, addr])

        client_thread.start()