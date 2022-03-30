from curses.ascii import DEL
import json
from urllib import request
import yaml 
import logging 
import socket 
DELIMETER = '\n'

class AmepadClient(object):
    
    def __init__(self, logger, machine_ip, machine_port):
        self.logger = logger
        self.machine_ip = machine_ip
        self.machine_port = machine_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
    
    def _connect(self):
        try:
            self.logger.info("Trying to connect to " + str(self.machine_ip) + ":" + str(self.machine_port))
            self.socket.connect((self.machine_ip, self.machine_port))
            self.connected = True 
            return True 
        except socket.error as ex:
            self.debug("Failed to connect. Exception: " + str(ex))
            # close connection
            self.socket.close()
            self.connected = False
            return False
    
    def _disconnect(self):
        self.socket.close()
        self.connected = False
    
    def _sendCommandImp(self, cmd):
        try:
            if self.connected == False:
                return None 
                
            self._sendRequest(cmd)
            for line in self._readline():
                line = line.decode('gb18030', 'ignore').encode('utf-8')
                self.logger.debug(line)
                return line
                
        except BaseException as ex:
            self.logger.error("Could not send Command {}: {}\n".format(cmd, ex))
            return None 
    
    def get_status_data(self, request):
        status_data = self._sendCommandImp(request)
        return status_data
            
    def get_info_data(self):
        info_data = self._sendCommandImp(request)
        return info_data
    
    def _sendRequest(self, cmd):
        request = cmd + DELIMETER
        self.socket.sendall(request)
    
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
    