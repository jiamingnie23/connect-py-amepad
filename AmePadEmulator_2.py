import logging
import random
import socket
import sys
import threading
import time

from enum import Enum 
from adapter_lib import Server
from adapter_lib.utilities import getTime
import random 

class StatusCode(Enum):
    StandBy = 1
    Printing = 2 #Stated or Not 
    Paused = 3 
    
class Machine(object):
    def run(self, totalTime):
        pass 
    
    def GetMachineStatus(self):
        pass 

    def StartJob(self):
        pass 
    
    def StopJob(self):
        pass 
    
    def PauseJob(self):
        pass
    
    def ResumeJob(self):
        pass 
    
    
class MachineImpl(Machine) :
    def __init__(self) :
        self.name = "AMPS1200"
        self.ip = "192.168.0.2"
        self.StatusCode = StatusCode.StandBy
        self.estimatedDuration = 0
        self.totalLayers = 0
        self._reset()
        super(MachineImpl, self).__init__()
        
    def _prepare(self, progress) :
        self.StatusCode = StatusCode.Preparation
        
    def _doWorkBefore(self, progress) :
        self.StatusCode = StatusCode.Working
        self.currentLayer = int(progress * self.totalLayers / 2)


    def _doWorkAfter(self, progress) :
        self.StatusCode = StatusCode.Working
        self.currentLayer = self.totalLayers / 2 + int(progress * self.totalLayers / 2)

    def _repair(self, progress) :
        self.StatusCode = StatusCode.Repair

    def _compelte(self, progress) :
        self.StatusCode = StatusCode.Complete

    def _reset(self) :
        self.StatusCode = StatusCode.StandBy
        self.startTime = getTime()
        self.currentLayer = 0
        self.totalLayers = random.randint(500, 1600)

    def GetStatusCode(self) :
        return self.StatusCode

    def GetOxygenValue(self) :
        return self.OxygenValue

    def GetCurrentLayer(self) :
        return self.currentLayer

    def GetTotalLayers(self) :
        return self.totalLayers

    def GetStartTime(self) :
        return self.startTime

    def GetEstimateDuration(self) :
        return self.estimatedDuration

    def run(self, totalTime) :
        steps = 100
        self.estimatedDuration = totalTime * (self.workTimeBeforeError + self.workTimeAfterError)
        while True :
            time.sleep(10)

            for i in range(0, steps) :
                self._prepare(1.0 * (i + 1) / steps)
                time.sleep(self.preparationTime * totalTime / steps)

            for i in range(0, steps) :
                self._doWorkBefore(1.0 * (i + 1) / steps)
                time.sleep(self.workTimeBeforeError * totalTime / steps)

            for i in range(0, steps) :
                self._repair(1.0 * (i + 1) / steps)
                time.sleep(self.repairTime * totalTime / steps)

            for i in range(0, steps) :
                self._doWorkAfter(1.0 * (i + 1) / steps)
                time.sleep(self.workTimeAfterError * totalTime / steps)

            for i in range(0, steps) :
                self._compelte(1.0 * (i + 1) / steps)
                time.sleep(self.completeTime * totalTime / steps)

            self._reset()
            
    
#####################################################
# The request and response configuration
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

# class BulkRequest(object):
#     def __init__(self):
#         self.simpleRequest = {
#             "?Q100": "SERIAL NUMBER, 1234567",
#             "?Q101": "SOFTWARE VERSION, 100.16.000.1031",
#             "?Q102": "MODEL, CSMD-G2",
#             "?Q104": "MODE, ZERO",
#             "?Q200": self.toolChangesFunc,
#             "?Q201": self.toolUsedFunc,
#             "?Q300": "P.O. TIME, 06282:17:13",
#             "?Q301": "C.S. TIME, 00098:18:29",
#             "?Q303": "LAST CYCLE, 00000:00:13",
#             "?Q304": "PREV CYCLE, 00000:00:01",
#             "?Q402": "M30 #1, 380",
#             "?Q403": "M30 #2, 380",
#             "?Q500": self.programFunc
#         }

#     def toolChangesFunc(self):
#         return "TOOL CHANGES, " + str(random.randint(9, 15))

#     def toolUsedFunc(self):
#         return "USING TOOL, " + str(random.randint(1, 5))

#     def programFunc(self):
#         status = ['IDLE', "FEED HOLD"]
#         return "PROGRAM, MDI, %s, PARTS, %s" % (status[random.randint(0, 1)], str(random.randint(1, 50)))

#     def isInterested(self, req, action) :
#         if req in self.simpleRequest:
#             return True

#         return False

#     def GetResponse(self, req, action) :
#         res = self.simpleRequest[req]
#         if (callable(res)):
#             return StringResponse(res())
#         return StringResponse(res)

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
        # self.serverConfiguration.AddRequest(BulkRequest())
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

def StartEmulatorTCPServer(host, port) :
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )

    logger = logging.getLogger('TEST EmulatorTCPServer')
    msg = "Start Shining TCP server on host:%s, port:%s\n" % (host, port)
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

if __name__ == "__main__" :
    argv_par = sys.argv

    logger = logging.getLogger('AmePad TCP Emulator ')
    #logger.setLevel(logging.INFO)

    for t in argv_par:
        logger.debug("ARGV: %s" % (t, ))

    if len(argv_par) <= 2:
        usage()
        sys.exit(0)

    host = argv_par[1]
    port = int(argv_par[2])
    StartEmulatorTCPServer(argv_par[1], port)
