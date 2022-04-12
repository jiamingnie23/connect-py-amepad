import socket
import json 
import ast
DELIMETER = '\n'

class AmepadClient(object):
    
    def __init__(self, logger, host, port):
        self.logger = logger
        self.host = host 
        self.port = port
        
    def _sendCommandImp(self, command):
        try:
            client_socket = socket.socket()  # instantiate
            client_socket.connect((self.host, self.port))  # connect to the server
            client_socket.send(command.encode())  # send message
            resp = client_socket.recv(1024).decode()  # receive response
            print('Received from server: ' + resp)  # show in terminal
            client_socket.close()  # close the connection
            return resp

        except BaseException as ex:
            self.logger.error("Could not send Command {}: {}\n".format(command, ex))
            return None 
    
    def get_status_data(self):
        request = "getstatus"
        status_data = self._sendCommandImp(request)
        status_data = self._convert_str_to_dict(status_data)
        return status_data
            
    def get_info_data(self):
        request = "getinfo"
        info_data = self._sendCommandImp(request)
        info_data = self._convert_str_to_dict(info_data)
        return info_data
    
    def _convert_str_to_dict(self, msg):
        if msg is None:
            return msg 
        else:
            first_idx = msg.find("{")
            msg = msg.replace("\n","")
            msg = msg.replace("\r","")
            sub_msg = msg[first_idx:]
            #msg_in_dict = json.loads(sub_msg)
            msg_in_dict = ast.literal_eval(sub_msg)
            return msg_in_dict
    
    def _template_data(self, type="info"):
        if type == "info":
            template_info = {
            "Name": None, 
            "IP": None,
            "MAC": None
            }
            return template_info
        else:
            template_status = {
            "progress": None,
            "used": None,
            "left": None,
            "currentfile": None,
            "started": None,
            "paused": None,
            "ErrorCode": None
             }
    
            return template_status