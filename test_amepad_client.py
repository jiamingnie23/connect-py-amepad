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

def test_info_data():
    info_data_raw = amepad_client.get_info_data()
    assert type(info_data_raw) == dict
    assert "IP" in info_data_raw
    assert "MAC" in info_data_raw
    assert "Name" in info_data_raw

def test_status_data():
    status_data_raw = amepad_client.get_status_data()
    assert type(status_data_raw) == dict 
    assert "paused" in status_data_raw
    assert "used" in status_data_raw
    assert "started" in status_data_raw
    assert "currentfile" in status_data_raw
    assert "ErrorCode" in status_data_raw
    assert "progress" in status_data_raw
    assert "left" in status_data_raw
