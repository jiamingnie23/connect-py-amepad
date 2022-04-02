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

def test_status_data():
    amepad_client._connect()
    status_data_raw = amepad_client.get_status_data()
    assert type(status_data_raw) == str 

def test_info_data():
    info_data_raw = amepad_client.get_info_data()
    assert type(info_data_raw) == str 

def test_amepad_client():
    amepad_client = get_sample_amepad_client()
    #amepad_client._connect()
    get_status_cmd = 'getstatus'
    #get_info_cmd = 'getinfo'
    get_status_res = amepad_client.get_status_data(get_status_cmd)
    print("Amepad Status Data: %s " % str(get_status_res))
    #get_info_res = amepad_client.get_info_data(get_info_cmd)
    #print("Amepad Info Data: " % str(get_info_res))


if __name__ == "__main__":
    test_amepad_client()