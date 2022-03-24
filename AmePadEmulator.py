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


if __name__ == "__main__":
    time_in_sec = 2500
    