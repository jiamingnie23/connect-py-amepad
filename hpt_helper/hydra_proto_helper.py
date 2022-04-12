import socket
from time import timezone, sleep
import Queue
import threading
import os

from utils import Utils
from client import Client
from repeater_timer import RepeatedTimer

from hydraproto.Message import Message
from hydraproto.Event import Event
from hydraproto.Sample import Sample
from hydraproto.RegisterDevice import RegisterDevice

class HydraProtoHelper():

    def __init__(self, killer, logger, dataitems, printer_info, hydra_client, **additional_params):
        self.killer = killer
        self.queue = Queue.Queue()
        self.logger = logger
        self.dataitems = dataitems        
        self.hpt_client = None
        self.reg_timer = None
        self.hpt_connection_timer = None
        self.hpt_connection_timer_initiated = False
        self.device_uuid = None
        self.hpt_host = "localhost"
        self.hpt_port = 1935
        self.hpt_hearbeat_interval = 30
        self.hpt_connection_retry_interval = 5

        self.__read_additional_information(**additional_params)
        self.__set_printer(printer_info) 
        self.__init_hpt_params(hydra_client)
        self.__intiate_processing_queue()
        self.__intialize_hydra_proto_client()
        self.__device_registration()
        
        

    def add_messages(self, messages):
        """ Process the dict based messages in individual hydra proto messsages """
        if messages:
            self.queue.put(messages)

    def __intialize_hydra_proto_client(self):
        try:            
            self.logger.info("Attempting to connect to HPT...")
            self.hpt_client = Client(host=self.hpt_host, port=self.hpt_port, logger=self.logger)
            self.hpt_connection_timer_initiated = False
            self.logger.info("Connected to Hydra Proto Server...")

            if self.hpt_connection_timer:
                self.hpt_connection_timer.stop()

            self.__registration_heartbeat()            
        except Exception as ex:
            self.logger.error('Failed to connect to Hydra Proto with %s : %s, reason %s' % (self.hpt_host, self.hpt_port, ex))
            self.__reinitiate_client()


    def __registration_heartbeat(self):
        
        if self.hpt_client and self.hpt_client.sock:
            self.reg_timer = RepeatedTimer(self.hpt_hearbeat_interval, self.__device_registration)
            timer_thread = threading.Thread(target=self.__monitor_timer)
            timer_thread.start()   

    def __getServiceIP(self):
        val = os.environ.get('OQTON_DEVICE_ID', None)
        return val if val else Utils.get_host_ip_v4_addr()

    def __device_registration(self):
        """
        Description: Device registration message. Periodically sending this message also acts as a heart beat mechanism
        """
        self.logger.info("invoking device registration")
        
        try:
            rd_msg = RegisterDevice(
                timestamp=Utils.get_formatted_datetime(),
                device=self.device,
                ipv4=self.__getServiceIP(),
                model=self.printer_info.get('model'),
                submodel=0,
                timezone=Utils.get_system_time_zone())

            self.__send_message(rd_msg.to_json())    
        except Exception as ex:
            self.logger.error("Device registration failed: %s" % ex)

    def __set_printer(self, printer_info):
        self.printer_info = printer_info
        pname = self.device_uuid if self.device_uuid else printer_info.get('name')
        self.device = '-'.join([str(printer_info.get('model')), pname])

    def __init_hpt_params(self, hydra_client):
        """Initial the host and port to connect to host"""
        self.hpt_host = hydra_client.get('host')
        self.hpt_port = hydra_client.get('port')
        self.hpt_hearbeat_interval = hydra_client.get('heartbeatInterval')
        self.hpt_connection_retry_interval = hydra_client.get('retryInterval')

    def __intiate_processing_queue(self):
        """ Thread based processing of the queue """
        threading.Thread(target=self.__process_queue_messages).start()

    def __process_queue_messages(self):        
        while not self.killer.is_set():
           if not self.queue.empty():
               try:
                   msg = self.queue.get()
                   self.logger.info("msg: %s" % msg)
                   if isinstance(msg, dict):
                       self.__dict_to_data_item(msg)
               except Exception as e:
                    self.logger.error("Failed to process HPT msg: %s" % e)

    def __dict_to_data_item(self, dict_obj):
        """ converts the dictionary based properties into individual data items """
        timestamp =  Utils.get_formatted_datetime()

        for key in dict_obj:           
            
            try:
                value = dict_obj[key]                
                match = self.__filter(key, value)

                if hasattr(match, 'additional_information'):
                    self.__form_hpt_response(self.device, key, value, match.additional_information.get('data_type'), timestamp)                
            except Exception as x:
                self.logger.error(x)           
                

    def __filter(self, key, value):
        match = list(filter(lambda x: (x.name == key or x.name == value), self.dataitems))
        return match[0] if match else None

    def __is_data_type_long(self, data_type):
        return True if "NUM" in data_type else False        

    def __form_hpt_response(self, device, key, value , data_type, timestamp):
        """
        Form the respective Hydra Proto Message based on data type mapping        
        """
        hpt_resp = None
        if "SAMPLE" in data_type:
            htp_resp = Sample(timestamp=timestamp, device=device, uuid=key, value=value, int_is_long=self.__is_data_type_long(data_type))
        elif "EVENT" in data_type:
            htp_resp = Event(timestamp=timestamp, device=device, uuid=key, value=self.__normalize_value(value, data_type), int_is_long=self.__is_data_type_long(data_type))
        elif "MESSAGE" in data_type:
            htp_resp = Message(timestamp=timestamp, native_code="", device=device, uuid=key, message=value, int_is_long=self.__is_data_type_long(data_type))           
       
        if htp_resp:
            self.__send_message(htp_resp.to_json())

    def __normalize_value(self, value, datatype):
        """
        Conversion to values to HPT supported forms
        i.e. Boolean is represented by Int
        """
        if "INT" in datatype and type(value) is bool:
            return int(value)
        return value

    def __send_message(self, message):
        try:
            self.logger.info('HPT message %s' % message)
            if self.hpt_client and self.hpt_client.sock:
                self.hpt_client.Send(message)
            else:
                self.__reinitiate_client()        
        except Exception as ex:
            self.logger('Failed to send message to HPT: %s, \n reason: %s' % (message, ex))            
            self.__reinitiate_client()        

    def __reinitiate_client(self):
        if self.reg_timer:
            self.reg_timer.stop()
        self.__try_clear_previous_hpt_conn()
        if not self.hpt_connection_timer_initiated:
            self.hpt_connection_timer = RepeatedTimer(self.hpt_connection_retry_interval, self.__intialize_hydra_proto_client)           
            self.hpt_connection_timer_initiated = True 
            
    def __monitor_timer(self):
        while not self.killer.is_set():
            sleep(0.1)
            pass

        if self.killer.is_set():
            self.reg_timer.stop()

            if self.hpt_connection_timer:
                self.hpt_connection_timer.stop()

    def __try_clear_previous_hpt_conn(self):
        if self.hpt_client:
            try:
                self.hpt_client.Disconnect()
            except Exception as ex:
                self.logger.error('HPT connection cleanup failed: %s' % ex)

    def __read_additional_information(self, additional_params):
        try:
            config = additional_params.get('config')
            
            if hasattr(config, 'device_uuid'):
                self.device_uuid = config.device_uuid

            
        except Exception as ex:
            self.logger.error('could not read config: %s' % ex)