import socket
import datetime
import os
from time import gmtime, strftime

class Utils():
    @staticmethod
    def get_host_ip_v4_addr():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        return local_ip

    @staticmethod
    def get_formatted_datetime():
        """return the current UTC date time in ISO format"""
        return datetime.datetime.utcnow().isoformat()

    @staticmethod
    def get_environ_var(key, default=None):
        return os.environ.get(key, default) 

    @staticmethod
    def get_system_time_zone():
        return strftime("%z", gmtime())