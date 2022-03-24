import logging
import random
from signal import pause
from decimal import Decimal
import socket
import sys
import threading
import time

from enum import Enum 
from adapter_lib import Server

TIME_PER_LAYER = 2 #2 seconds for printing 1 layer 

class AmePadMachine(object):
    def __init__(self, name="AMPS2000", ip="0.0.0.1",mac_address=""):
        self.name = name 
        self.ip = ip 
        self.mac_address = mac_address
        self.error_code = 000
        self.current_job_file = ""
        # for printing state 
        self.__init_status_data()
        self.__init_msg_body()
    
    def __init_msg_body(self):
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
        if file_name_split[-1] == ".gcode":
            self.current_job_file = file_name
            return "Upload Job File Successfully"
        else:
            return "File extension is not .gcode. Please upload it again."
    
    def open_file(self):
        open_file_msg = "open " + self.current_job_file
        if len(self.current_job_file) > 0:
            ok_msg = "ok: open file successfully"
            msg = open_file_msg + "\n" + ok_msg  
            self.is_file_opened = True      
            return msg 
        else:
            fail_msg = "open file failed."
            msg = open_file_msg + "\n" + fail_msg
            return fail_msg
    
    def get_machine_info(self):
        pass 
    
    def start_job(self):
        open_file_msg = self.open_file()
        start_job_msg = ""
        if "fail" in open_file_msg:
            start_job_msg = "Open File Failed. Cannot Start Job."
        else:
            if self.start_job_status == True:
                start_job_msg = "A job is already running."
            else:
                start_job_msg = "ok: start/resume successfully."
                self.start_job_status = True 
                # initialize the layers 
                self.total_layers = random.randint(200,2000)
                
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
    
    def get_machine_status(self):
        machine_status_msg = "status" + str(self.status_msg_body)
        return machine_status_msg 
    
    def get_machine_info(self):
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

#####################################################
# The request and response configuration
class Request(object) :
    def __init__(self, req, action, response):
        self.req = req
        self.action = action
        self.response = response

    def isInterested(self, req, action) :
        if (self.req.lower() == req.lower() and self.action.lower() == action.lower()) :
            return True
        return False

    def GetResponse(self) :
        return self.response

class BulkRequest(object):
    def __init__(self):
        self.simpleRequest = {
            "?Q100": "SERIAL NUMBER, 1234567",
            "?Q101": "SOFTWARE VERSION, 100.16.000.1031",
            "?Q102": "MODEL, CSMD-G2",
            "?Q104": "MODE, ZERO",
            "?Q200": self.toolChangesFunc,
            "?Q201": self.toolUsedFunc,
            "?Q300": "P.O. TIME, 06282:17:13",
            "?Q301": "C.S. TIME, 00098:18:29",
            "?Q303": "LAST CYCLE, 00000:00:13",
            "?Q304": "PREV CYCLE, 00000:00:01",
            "?Q402": "M30 #1, 380",
            "?Q403": "M30 #2, 380",
            "?Q500": self.programFunc
        }

    def toolChangesFunc(self):
        return "TOOL CHANGES, " + str(random.randint(9, 15))

    def toolUsedFunc(self):
        return "USING TOOL, " + str(random.randint(1, 5))

    def programFunc(self):
        status = ['IDLE', "FEED HOLD"]
        return "PROGRAM, MDI, %s, PARTS, %s" % (status[random.randint(0, 1)], str(random.randint(1, 50)))

    def isInterested(self, req, action) :
        if req in self.simpleRequest:
            return True

        return False

    def GetResponse(self, req, action) :
        res = self.simpleRequest[req]
        if (callable(res)):
            return StringResponse(res())
        return StringResponse(res)

class StringResponse(object):
    def __init__(self, message):
        self.msg = message

    def GetResponse(self) :
       return self.msg


class ServerConfiguration(object) :
    def __init__(self) :
        self.requests = []

    def AddRequest(self, request) :
        if (request is not None) :
            self.requests.append(request)

    def ProcessRequest(self, req, action) :
        for _req in self.requests:
            if (_req.isInterested(req, action)) :
                return _req.GetResponse(req, action)

        return None
    
#######################################################
# The TCP Server
class EmulatorTCPServer(Server) :
    def __init__(self, host, port, lock) :
        self.ExitAdapterFlag = True
        self.serverConfiguration = ServerConfiguration()
        self.machine = MachineImpl()

        # Read configuration from yaml, now just create it as Hard coded
        self.serverConfiguration.AddRequest(BulkRequest())
        super(EmulatorTCPServer, self).__init__(host, port, lock)

    # override the listen function
    def listen2(self, message):
        self.sock.listen(10)
        while True:
            client, address = self.sock.accept()
            client.settimeout(600)
            self.logger.debug('Client connected at: %s:%s',address[0],address[1])
            #client.sendall(message)
            port = address[1]
            self.mClientList[port] = client
            threading.Thread(target = self.communicateWithClient2,args = (client,address)).start()

            self.t1 = threading.Thread(target=self.machine.run(60), args=[self])
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
                    if '* PING' in data:
                        heartbeats = True
                        data = ""
                        self.heartbeat_count = self.heartbeat_count + 1
                        buff = '* PONG 30000\n'
                        self.logger.debug(str(self.heartbeat_count) + " " + buff.replace('\n', '\\n'))
                        client.sendall(buff)
                    else :
                        if (self.ProcessUnknownData(client, data)) :
                            data = ''
                except:
                    pass

        except Exception as e:
            self.logger.debug(e)
            client.close()
            return False

    def ProcessUnknownData(self, client, data):
        if ('\n' in data) :
            message = data
            self.logger.debug("EmulatorTCPServer::DealWithUnknownData")

            try :
                # Deal with request, remove the \r, \n and space
                message = message.replace('\n', '').replace('\r', '').replace(' ', '')
                messages = message.split(',')
                if ((messages is not None) and (len(messages) >= 1)) :
                    if len(messages) > 1:
                        action = messages[1]
                    else:
                        action = None
                    response = self.serverConfiguration.ProcessRequest(messages[0], action)
                    if (response is not None) :
                        responseMsg = str(response.GetResponse())
                        #print responseMsg
                        client.sendall(responseMsg + '\n')
                    else:
                        client.sendall("?," + messages[0] + '\n')
                    return True

                # Wow, unknonw data
                client.sendall('PLC:Alive\n')
            except BaseException as e:
                self.logger.debug("EmulatorTCPServer::Process data met exception: " + e)
            finally :
                return True

        # Not end input, let parent deal with it
        return False

    def close(self) :
        pass

if __name__ == "__main__":
    time_in_sec = 2500
    