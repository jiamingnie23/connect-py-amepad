import socket
import json
DELIMETER = '\n'

class AmepadClient(object):
    
    def __init__(self, logger, machine_ip, machine_port):
        self.logger = logger
        self.machine_ip = machine_ip
        self.machine_port = machine_port
        #self.tcp_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #self.tcp_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.connected = False
    
    def _connect(self):
        try:
            self.logger.info("Trying to connect to " + str(self.machine_ip) + ":" + str(self.machine_port))
            self.tcp_client.connect((self.machine_ip, self.machine_port))
            self.connected = True 
            return True 
        except socket.error as ex:
            self.logger.debug("Failed to connect. Exception: " + str(ex))
            # close connection
            self.tcp_client.close()
            self.connected = False
            return False
    
    def _disconnect(self):
        self.tcp_client.close()
        self.connected = False
    
    def _sendCommandImp(self, cmd):
        try:
            self._connect() #connect to server
            #self._sendRequest(cmd)
            return self._sendRequet2(cmd)
            # for line in self._readline():
            #     line = line.decode('gb18030', 'ignore').encode('utf-8')
            #     self.logger.debug(line)
            #     return line
                
        except BaseException as ex:
            self.logger.error("Could not send Command {}: {}\n".format(cmd, ex))
            return None 
    
    def get_status_data(self, request):
        # self._sendRequest(request)
        # status_data = self._receive_data()
        status_data = self._send_request_and_get_data(request)
        status_data = self._convert_str_to_dict(status_data)
        return status_data
            
    def get_info_data(self, request):
        # send message first: 1. establish connection 2. send msg 
        # receive msg: 1. establish connection 2. receive msg 
        info_data = self._sendCommandImp(request)
        info_data = self._convert_str_to_dict(info_data)
        return info_data 
    
    def _convert_str_to_dict(self, msg):
        if msg is None:
            return msg 
        else:
            first_idx = msg.find("{")
            sub_msg = msg[first_idx:]
            msg_in_dict = json.loads(sub_msg)
            return msg_in_dict
    
    # new method 
    def _send_request_and_get_data(self, cmd):
        sock_local = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock_local.setblocking(0) # non-blocking 
        sock_local.connect((self.machine_ip, self.machine_port))
        sock_local.send(cmd.encode())
        while True:
            # sock_local = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            # sock_local.setblocking(0) # non-blocking 
            # sock_local.connect((self.machine_ip, self.machine_port))
            # sock_local.send(cmd.encode())
            response = sock_local.recv(1024)
            data = response.decode()
            print(data)
            return data 
        
    # send Request First 
    def _sendRequest(self, cmd):
        self._connect()
        if self.connected == False:
            self.logger.debug("Connection to TCP server met exception.")
        else:
            request = cmd + DELIMETER
            self.tcp_client.sendall(request.encode())
            self._disconnect()
    
    def _receive_data(self):
        while True:
            try:
                self._connect()
                response = self.tcp_client.recv(1024)
                data = response.decode()
                self._disconnect()
                return data 
            except socket.timeout as ex:
                self.logger.debug("Client connection met timeout exception %s " % str(ex))
                return None # None data 
    
    def _sendRequet2(self, cmd):
        buffering = True 
        BUFFER_SIZE = 4096
        request = cmd + '\r' + '\n'
        
        while buffering:
            self.tcp_client.send(request)
            response = self.tcp_client.recv(BUFFER_SIZE)
            data = response.decode()
            return data 
        #self.tcp_client.close()
        self._disconnect()
    
    
    def _readline(self):
        MAX_LINE_LENGTH = 4096000
        BUFFER_SIZE = 4096
        buffer = self.socket.recv(BUFFER_SIZE)
        buffering = True
        while buffering:
            if DELIMETER in buffer:
                (line, buffer) = buffer.split(DELIMETER, 1)
                yield line
            else:
                more = self.sock.recv(BUFFER_SIZE)
                if not more:
                    buffering = False
                else:
                    buffer += more
                if len(buffer) >= MAX_LINE_LENGTH:
                    buffering = False
        if buffer:
            yield buffer
    