import socket

"""
"""


class Client(object):

    def __init__(self, logger, host, port):
        """
        """
        self.logger = logger
        self.host = host
        self.port = port
        self.sock = None
        self.Connect()

    def Connect(self):
        """
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info("Attempting to connect to %s:%d" % (self.host, self.port)) 
        self.sock.connect((self.host, self.port))

    def Send(self, message):
        """
        """
        self.sock.sendall(str(message) + '\n')

    def Disconnect(self):
        """
        """
        self.logger.info("Attempting to close connection to %s:%d" % (self.host, self.port)) 
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.sock = None