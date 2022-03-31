import logging
import random
from decimal import Decimal
import socket
import sys
import threading
import time

from adapter_lib import Server

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
            "pasused": self.pause_job_status,
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

# #####################################################
# # The request and response configuration
# class Request(object) :
#     def __init__(self, req, action, response):
#         self.req = req
#         self.action = action
#         self.response = response

#     def isInterested(self, req, action) :
#         if (self.req.lower() == req.lower() and self.action.lower() == action.lower()) :
#             return True
#         return False

#     def GetResponse(self) :
#         return self.response

# class StringResponse(object):
#     def __init__(self, message):
#         self.msg = message

#     def GetResponse(self) :
#        return self.msg

# class ServerConfiguration(object) :
#     def __init__(self) :
#         self.requests = []

#     def AddRequest(self, request) :
#         if (request is not None) :
#             self.requests.append(request)

#     def ProcessRequest(self, req, action) :
#         for _req in self.requests:
#             if (_req.isInterested(req, action)) :
#                 return _req.GetResponse(req, action)

#         return None

class TCPEmulator(object):
    def __init__(self, host, port):
        self.machine = AmepadMachine()
        self.host = host 
        self.port = port 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def start_server(self):
        self.server.connect(self.host, self.port)
        

#######################################################
# The TCP Server
class EmulatorTCPServer(Server):
    def __init__(self, host, port, lock) :
        self.ExitAdapterFlag = True
        #self.serverConfiguration = ServerConfiguration()
        self.machine = AmepadMachine()

        # Read configuration from yaml, now just create it as Hard coded
        #self.serverConfiguration.AddRequest(BulkRequest())
        super(EmulatorTCPServer, self).__init__(host, port, lock)

    # override the listen function
    def listen2(self, message):
        self.sock.listen(10)
        while True:
            client, address = self.sock.accept()
            #client.settimeout(600)
            self.logger.debug('Client connected at: %s:%s',address[0],address[1])
            #client.sendall(message)
            port = address[1]
            self.mClientList[port] = client
            threading.Thread(target = self.communicateWithClient2,args = (client,address)).start()

            self.t1 = threading.Thread(target=self.machine.run())
            self.t1.setDaemon(True)
            self.t1.start()

    def communicateWithClient2(self, client, address):
        self.heartbeat_count = 0
        try:
            self.logger.debug('TCPhandle')
            data = ""
            buff = ""
            heartbeats = False
            while True:
                try:
                    buff = client.recv(1024)
                except socket.timeout as e:
                    if not heartbeats:
                        continue
                    else:
                        self.logger.debug(e)
                        client.close()
                        return False

                if not buff: break
                with self.lock:
                    data = data + buff
                self.logger.debug('recv()->"%s"', buff.replace('\n','\\n'))

                try:
                    # Command: 
                    # Open File 
                    # Start 
                    # Pause 
                    # Resume 
                    # getstatus
                    # getinfo
                    resp_msg = ""
                    data = data.replace("\n","")
                    data = data.replace("\r","")
                    print(data)
                    if data == "getstatus":
                        resp_msg = self.machine.get_machine_status()
                    elif data == "getinfo":
                        resp_msg = self.machine.get_machine_info()
                    elif data == "start":
                        resp_msg = self.machine.start_job()
                    elif data == "pause":
                        resp_msg = self.machine.pause_job()
                    elif data == "stop":
                        resp_msg = self.machine.stop_job()
                    elif data == "resume":
                        resp_msg = self.machine.resume_job()
                    elif "open" in data:    
                        data_split = data.split()  
                        try:     
                            open_command = data_split[0]
                            file_name = data_split[1]    
                            resp_msg = self.machine.open_file(file_name)       
                        except Exception as e:
                            self.logger.error("Met Exception in Command: %s " %str(e))
                            resp_msg = "Open File Format is not right"
                    else:
                        resp_msg = "Invalid Command."
                    
                    data = "" #clear the data
                    '''send back the message'''
                    self.logger.info("Process Commands")
                    resp_msg = resp_msg + "\n"
                    client.sendall(resp_msg) 
                    
                except:
                    pass

        except Exception as e:
            self.logger.debug(e)
            client.close()
            return False

    def close(self) :
        pass

def StartEmulatorTCPServer(host, port) :
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )

    logger = logging.getLogger('TEST EmulatorTCPServer')
    msg = "Start Amepad TCP server on host:%s, port:%s\n" % (host, port)
    logger.debug(msg)

    lock = threading.Lock()
    server = EmulatorTCPServer(host, port, lock)
    t1 = threading.Thread(target=server.listen2, args=[msg])
    t1.setDaemon(True)
    t1.start()

    while server.ExitAdapterFlag:
        time.sleep(1)

    # Clean up
    logger.debug('closing socket')
    server.close()
    logger.debug('done')

def usage() :
    print("That is not proper usage: \n")
    print('python TCPServerEmulator.py host port\n')

if __name__ == "__main__":
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
    StartEmulatorTCPServer(argv_par[1], port)
    