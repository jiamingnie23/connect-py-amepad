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

    def initialize(self):
        try:
            self.logger.info("Initialize data gather ")
            return True

        except Exception as e:
            self.logger.error('[initialize]: got the exception: %s' % str(e))
            return False

    def _connect(self):
        return True 
    
    def _disconnect(self):
        pass 
    
    def _gather_data_helper(self, data, use_mock=False):
        for key in data:
            if use_mock:
                self.adapter.set_di_unavailable(key)
            else:
                value = data.get(key)
                if value is not None:
                    self.adapter.set_di_value(key,value)
                else:
                    self.adapter.set_di_unavailable(key)

        self._convert_to_hpt(processed_msgs=data)

    def _gatherdata(self):
        try:
            '''Machine Status Data'''
            # get machine status data
            is_avail = False
            try:
                use_mock = False
                machine_status_data = self.amepad_client.get_status_data()
                if machine_status_data is None:
                    machine_status_data = self.amepad_client._template_data(type="status")
                    use_mock = True
                self._gather_data_helper(machine_status_data, use_mock)
                is_avail = is_avail or (not use_mock)
            except BaseException as e: 
                self.logger.error('[_gatherdata] Retrieve Machine Status Data met Exception %s' % str(e))

            # get machine info data
            try:
                use_mock = False
                machine_info_data = self.amepad_client.get_info_data()
                if machine_info_data is None:
                    machine_info_data = self.amepad_client._template_data(type="info")
                    use_mock = True
                self._gather_data_helper(machine_info_data, use_mock)
                is_avail = is_avail or (not use_mock)
            except BaseException as e: 
                self.logger.error('[_gatherdata] Retrieve Machine Info Data met Exception %s' % str(e))

            if is_avail:
                self.adapter.set_di_value('avail', 'AVAILABLE')
            else:
                self.adapter.set_di_unavailable('avail')
            self.adapter.send_changed_data()

            self.logger.info(" Start Fecthing and Sending Data .... ")

        except BaseException as e:
            self.adapter.set_di_unavailable('avail')
            self.logger.error('[_gatherdata]: got the exception %s' % e)
        finally:
            self.delayPoll()

    
    def serve(self):
        try:
            while self.exitAdapterFlag:
                self._gatherdata()
            
            self._disconnect()
        except KeyboardInterrupt:
            self._destroy_hpt()
        except Exception as e:
            self.logger.error('[serve]: got the exception %s' % e)
    
    def run(self):
        self.serve()
    
    def delayPoll(self):
        time.sleep(self.config.scandelay / 1000.0)
    
    ### Hydra Proto ###
    def _initialize_hpt(self):
        if not self.config.hydraClient.get("enabled"): 
            self.logger.info('Hydra client is not enabled.')
            return

        """ Initialize the HPT Converter """
        self.killer = threading.Event()
        dataitems = self.adapter.dataitems_obj().dataitems()
        
        # additional_params can be used to be pass information without changing the signature of the default constructor
        additional_params = dict()
        additional_params.update({"config": self.config})
        
        self.hpt = HydraProtoHelper(
            killer=self.killer, 
            logger=self.logger, 
            dataitems=dataitems, 
            printer_info=self.config.printer, 
            hydra_client=self.config.hydraClient,
            additional_params=additional_params)

    def _convert_to_hpt(self, processed_msgs):
        if self.hpt:
            self.hpt.add_messages(messages= processed_msgs)

    def _destroy_hpt(self):
        if self.hpt:
            """Kills the threads/process spawned by HPT"""
            self.logger.info('sending kill')
            self.hpt.killer.set()