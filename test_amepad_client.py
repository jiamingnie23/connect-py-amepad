'''Unit Test Using PyTest'''
from AmePad_client import AmepadClient
import yaml 
import logging

def load_host_info(file='adapter.yaml'):
    try:
        with open(file, 'r') as f:
            doc = yaml.load(f)
    except IOError as e:
        print('parse file throw ' + e.strerror)
    
    ConnectionInfo = doc['connection']
    host = ConnectionInfo['host']
    port = ConnectionInfo['port']
    return host, port 
    
def get_sample_amepad_client():
    logger = logging.getLogger()
    host, port = load_host_info()
    amepad_client = AmepadClient(logger, host, port)
    return amepad_client

amepad_client = get_sample_amepad_client()

def test_basic_config()
