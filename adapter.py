from multiprocessing.connection import Connection
from adapter_lib import Adapter, Configuration, Condition, Conditions, DataItem, DataItems, Message, Messages, Server
import logging
import yaml


class AmepadConditions(Conditions):
    def __init__(self):
        self.__conditions = []
        super(AmepadConditions, self).__init__()

    def conditions(self):
        return self.__conditions

    def active_conditions(self):
        return self.__conditions

class AmepadDataItems(DataItems):
    def __init__(self):
        self.__dataitems = []
        super(AmepadDataItems, self).__init__()

    def add_di(self, dataItem):
        self.__dataitems.append(dataItem)

    def parse(self, file='adapter.yaml'):
        pass

    def dataitems(self):
        return self.__dataitems


class AmepadMessages(Messages):
    def __init__(self):
        self.__messages = []
        super(AmepadMessages, self).__init__()

    def messages(self):
        return self.__messages


class AmepadConfiguration(Configuration):
    def __init__(self):
        self.logger = logging.getLogger('Amepad __main__')
        super(AmepadConfiguration, self).__init__()

        # Connection Parameters:
        self.timeout = 100
        self.retryDelay = 3000
        self.maxConsecutiveFailNum = 5
        self.host = None 
        self.device_uuid = None 
        self.http_server_port = None 
        self.printer = None
        self.hydraClient = None
        self.hydraClient_enabled = False

    def parse(self, file='adapter.yaml'):
        self.logger.info('Parsing configuration file (' + file + ')')
        try:
            with open(file, 'r') as f:
                doc = yaml.load(f)
        except IOError as e:
            self.logger.error('parse file throw ' + e.strerror)
            raise

        try:
            super(AmepadConfiguration, self).parse(doc)
            ConnectionInfo = doc['connection']

            try:
                host = ConnectionInfo['host']
                self.host = host
            except KeyError as e:
                raise ValueError("Service Host Must be Addressed")
                
            try:
                port = ConnectionInfo['port']
                self.port = port
            except KeyError as e:
                pass 

            try: 
                self.timeout = ConnectionInfo['timeout']
            except KeyError as e:
                pass 

            try: 
                self.retryDelay = ConnectionInfo['retryDelay']
            except KeyError as e:
                pass 

            try:
                self.maxConsecutiveFailNum = ConnectionInfo['maxConsecutiveFailNum']
            except KeyError as e:
                pass 
                
            try:
                self.printer = doc['printer']                                
            except KeyError as e:
                raise KeyError("Printer name not defined %s" % self.printer)

            try:
                self.hydraClient = doc['hydraClient']   
                self.hydraClient_enabled = self.hydraClient['enabled']
                self.http_server_host = self.hydraClient['dmc_server_host']
                self.http_server_port = self.hydraClient['dmc_server_port']
                             
            except KeyError as e:
                raise KeyError("hydraClient not defined")

        except Exception as e:
            self.logger.error('HAASConfiguration.parse throw ' + e.message)


class AmepadAdapter(Adapter):
    def __init__(self, lock, logger, debug_mode=False):
        self.logger = logger
        self.debug_mode = debug_mode
        super(AmepadAdapter, self).__init__(AmepadConfiguration,
                                             AmepadDataItems, AmepadConditions, AmepadMessages, lock, debug_mode)

    def get_initial_message(self):
        try:
            return super(AmepadAdapter, self).get_initial_message()
        except Exception as e:
            self.logger.error('get_initial_message throw ' + e.message)
            return ""

    def find_by_name(self, collection, name):
        return next((x for x in collection if name == x.name), None)

    def _set_di(self, name, func):
        di = self.find_by_name(self.dataitems(), name)
        if not di:
            di = DataItem(name)
            self.dataitems().append(di)
        func(di)

    def set_di_value(self, name, value):
        self._set_di(name, lambda di: di.set_value(value))

    def set_di_unavailable(self, name):
        self._set_di(name, lambda di: di.set_unavailable())

    def _set_msg(self, name, func):
        msg = self.find_by_name(self.messages(), name)
        if not msg:
            msg = Message(name)
            self.messages().append(msg)
        func(msg)

    def set_msg_value(self, name, value):
        self._set_msg(name, lambda msg: msg.set_value(value))

    def set_msg_unavailable(self, name):
        self._set_msg(name, lambda msg: msg.set_unavailable())
