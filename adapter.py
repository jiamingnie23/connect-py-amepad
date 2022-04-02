from adapter_lib import Adapter, Configuration, Condition, Conditions, DataItem, DataItems, Message, Messages, Server
import threading
import logging
import sys
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

        #self.serialConfigEnabled = True

        #self.portName = None
        #self.buadRate = 9200
        #self.parity = 'N'
        #self.rtscts = False
        #self.xonxoff = False
        #self.rts = None
        #self.dtr = None

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

            try:
                self.serialConfigEnabled = doc['serial_connection'] is not None
                self.logger.info('serial connection enabled: ' + str(self.serialConfigEnabled))

                self.portName = doc['serial_connection']['name']

                # try:
                #     self.buadRate = doc['serial_connection']['baudrate']
                # except KeyError as e:
                #     pass

                # try:
                #     self.parity = doc['serial_connection']['parity']
                # except KeyError as e:
                #     pass

                # try:
                #     self.rtscts = doc['serial_connection']['rtscts']
                # except KeyError as e:
                #     pass

                # try:
                #     self.xonxoff = doc['serial_connection']['xonxoff']
                # except KeyError as e:
                #     pass

                # try:
                #     self.rts = doc['serial_connection']['rts']
                # except KeyError as e:
                #     pass

                # try:
                #     self.dtr = doc['serial_connection']['dtr']
                # except KeyError as e:
                #     pass

            except KeyError as e:
                self.serialConfigEnabled = False

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

    def set_condition_value(self, name, value):
        condition = self.find_by_name(self.conditions(), name)
        if not condition:
            condition = Condition(name)
            self.conditions_obj().add_condition(condition, self.conditions())
        condition.set_status(value)

