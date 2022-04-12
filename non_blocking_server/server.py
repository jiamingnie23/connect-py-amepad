import socket
import threading 
class server:
    def __init__(self):
        self.connect_flag = False
    
    def run_server(self):
        server_thread = threading.Thread(target=self.server_program_in_pack)
        server_thread.start()
    
    def server_program_in_pack(self):
        while True:
            self.server_program()

    def server_program(self):
        # get the hostname
        host = socket.gethostname()
        port = 8080  # initiate port no above 1024

        server_socket = socket.socket()  # get instance
        # look closely. The bind() function takes tuple as argument
        server_socket.bind((host, port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        server_socket.listen(2)
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                # if data is not received break
                break
            print("from connected user: " + str(data))
            data = "Hi this is sample response"
            conn.send(data.encode())  # send data to the client

        conn.close()  # close the connection

    
if __name__ == '__main__':
    tcp_server = server()
    tcp_server.run_server()