import threading 
import random
from decimal import Decimal
import socket
import threading
import time
import logging 
import sys 

TIME_PER_LAYER = 2 #2 seconds for printing 1 layer 

class AmepadMachine(object):
    def __init__(self, name="AMPS2000", ip="0.0.0.1",mac_address=""):
        self.name = name 
        self.ip = ip 
        self.mac_address = mac_address
        self.error_code = 000
        self.current_job_file = ""
        # for printing state 
        self.__init_status_data()
        self.__init_and_update_msg_body()
    
    def __init_and_update_msg_body(self):
        self.info_msg_body = {
            "Name": self.name, 
            "IP": self.ip,
            "MAC": self.mac_address
        }
        
        self.status_msg_body = {
            "progress": self.job_progress,
            "used": self.convert_time_format(self.used_time),
            "left": self.convert_time_format(self.remain_time),
            "currentfile": self.current_job_file,
            "started": self.start_job_status,
            "paused": self.pause_job_status,
            "ErrorCode": self.error_code
        }
    
    def __init_status_data(self):
        self.start_job_status = False 
        self.pause_job_status = False
        self.job_progress = 0 
        self.total_layers = 0
        self.printed_layers = 0
        self.used_time = 0
        self.remain_time = 0
    
    def convert_time_format(self, time_in_sec):
        h = time_in_sec // 3600
        m = time_in_sec % 3600 // 60
        s = time_in_sec % 3600 % 60
        return '{:02d}:{:02d}:{:02d}'.format(h, m, s)

    
    def add_file(self,file_name):
        file_name_split = file_name.split(".")
        if file_name_split[-1] == "gcode":
            self.current_job_file = file_name
            return "Upload Job File Successfully"
        else:
            return "File extension is not .gcode. Please upload it again."
    
    def open_file(self, file_name):
        # add/upload the file first, it will change the current
        # job file 
        if len(file_name) > 0:
            self.add_file(file_name)
            msg = ""
            if len(self.current_job_file) > 0:
                open_file_msg = "open " + self.current_job_file
                ok_msg = "ok: open file successfully"
                msg = open_file_msg + "\n" + ok_msg  
                self.is_file_opened = True  
            else:
                msg = "open file failed."    
            return msg 
        else:
            fail_msg = "open file failed."
            return fail_msg
            
    def start_job(self):
        open_file_msg = self.open_file(self.current_job_file)
        start_job_msg = ""
        if "fail" in open_file_msg:
            start_job_msg = "Open File Failed. Cannot Start Job."
        else:
            if self.start_job_status == True:
                start_job_msg = "A job is already running."
            else:
                start_job_msg = "ok: start/resume successfully."
                # initialize the layers 
                self.total_layers = random.randint(200,2000)
                self.start_job_status = True 
                
        return start_job_msg

    def pause_job(self):
        pause_job_msg = ""
        if self.pause_job_status == False:
            pause_job_msg = "Job already paused"
        else:
            pause_job_msg = "ok: pause successfully"
            self.pause_job_status = True 
        return pause_job_msg
    
    def resume_job(self):
        resume_job_msg = ""
        if self.start_job_status == False or self.pause_job_status == True:
            resume_job_msg = "No Job is running."
        elif self.pause_job_status == False:
            resume_job_msg = "ok: start/resume successfully."
            self.pause_job_status = True 
        return resume_job_msg
    
    def stop_job(self):
        stop_job_msg = ""
        if self.start_job_status == True:
            self.__init_status_data()
            stop_job_msg = "ok: stop successfully"
        else:
            stop_job_msg = "error: no job is running"
        return stop_job_msg
        
    def get_machine_status(self):
        self.__init_and_update_msg_body()
        machine_status_msg = "status" + str(self.status_msg_body)
        return machine_status_msg 
    
    def get_machine_info(self):
        self.__init_and_update_msg_body()
        machine_info_msg = "info" + str(self.info_msg_body)
        return machine_info_msg 
    
    def update_machine_status(self):
        if self.start_job_status == True:
            if self.pause_job_status == False:
                remain_layers = self.total_layers - self.printed_layers
                self.used_time = self.printed_layers * TIME_PER_LAYER
                self.remain_time = remain_layers * TIME_PER_LAYER
                job_progress = round(Decimal(self.printed_layers)/Decimal(self.total_layers),1)
                self.job_progress = job_progress
                time.sleep(TIME_PER_LAYER)
                self.printed_layers += 1
                if self.printed_layers > self.total_layers:
                    self.__init_status_data()
    
    def run(self):
        while True:
            self.update_machine_status()

class TCPServer(object):
    def __init__(self, host, port):
        self.host = host 
        self.port = port 
        self.amepad_machine = AmepadMachine()
        self.logger = logging.getLogger("Test Amepad Emulator")

    def run_server(self):
        self.logger.debug("Start Amepad TCP server on host:%s, port:%s\n" % (self.host, self.port))
        server_thread = threading.Thread(target=self._server_on_listen)
        server_thread.start()
        machine_thread = threading.Thread(target=self.amepad_machine.run())
        machine_thread.setDaemon(True)
        machine_thread.start()

    def _server_on_listen(self):
        server_socket = socket.socket()
        server_socket.bind((self.host, self.port))
        server_socket.listen(2)
        while True:
            self._server_communication(server_socket)

    def _server_communication(self, server_socket):
        # server_socket = socket.socket()
        # server_socket.bind((self.host,self.port))

        # server_socket.listen(2)
        # server_socket = socket.socket()
        # server_socket.bind((self.host, self.port))
        # server_socket.listen(2)
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        #while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        # if not data:
        #     # if data is not received break
        #     break
        # remove character 
        data = data.replace("\n","")
        data = data.replace("\r","")
        print("from connected user: " + str(data))
        self.logger.info("Process input: " + str(data))
        if data == "getstatus":
            resp_msg = self.amepad_machine.get_machine_status()
        elif data == "getinfo":
            resp_msg = self.amepad_machine.get_machine_info()
        elif data == "start":
            resp_msg = self.amepad_machine.start_job()
        elif data == "pause":
            resp_msg = self.amepad_machine.pause_job()
        elif data == "stop":
            resp_msg = self.amepad_machine.stop_job()
        elif data == "resume":
            resp_msg = self.amepad_machine.resume_job()
        elif "open" in data:    
            data_split = data.split()  
            try:     
                open_command = data_split[0]
                file_name = data_split[1]    
                resp_msg = self.amepad_machine.open_file(file_name)       
            except Exception as e:
                self.logger.error("Met Exception in Command: %s " %str(e))
                resp_msg = "Open File Format is not right"
        else:
            resp_msg = "Invalid Command."
        
        #data = "" #clear the data
        '''send back the message'''
        self.logger.info("Process Commands")
        resp_msg = resp_msg + "\n"

        #data = "Hi this is sample response"
        conn.send(resp_msg.encode())  # send data to the client
        
        conn.close()  # close the connection
    
def usage() :
    print("That is not proper usage: \n")
    print('python TCPServerEmulator.py host port\n')
    
if __name__ == '__main__':
    argv_par = sys.argv

    logger = logging.getLogger('Amepad Server Emulator')
    #logger.setLevel(logging.INFO)

    for t in argv_par:
        logger.debug("ARGV: %s" % (t, ))

    if len(argv_par) <= 2:
        usage()
        sys.exit(0)

    host = argv_par[1]
    port = int(argv_par[2])
    tcp_server = TCPServer(host, port)
    tcp_server.run_server()