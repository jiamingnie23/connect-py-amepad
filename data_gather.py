# -*- coding: UTF-8 -*-
from AmePad_client import AmepadClient
from fos_lib import SessionManager, RetryStrategy
import time 
from hpt_helper import HydraProtoHelper
import threading
DELIMETER = '\n'

class AmepadDataGather(object):
    def __init__(self, adapter, logger):
        self.adapter = adapter 
        self.config = self.adapter.configuration_obj()
        self.logger = logger
        self.exitAdapterFlag = True     
        self.__init_amepad_client()
    
    def __init_amepad_client(self):
        host = self.config.host 
        port = self.config.port 
        self.amepad_client = AmepadClient(self.logger, host, port)

    def _connect(self):
        return True 
    
    def _disconnect(self):
        pass 
    
    def _gatherdata(self):
        try:
            '''Machine Status Data'''
            try:
                machine_status_data = self.amepad_client.get_status_data()
                
        
        except BaseException as e:
            self.adapter.set_di_unavailable('avail')
            self.logger.error('[_gatherdata]: got the exception %s' % e)
        finally:
            self.delayPoll()

    
    def serve(self):
        pass 
    
    def run(self):
        pass 
    
    def deplayPoll(self):
        pass 
    
    ### Hydra Proto ### 
    def __initialize_hpt(self):
        pass 
    
    def _convert_to_hpt(self):
        pass 
    
    def _destory_hpt(self):
        pass 