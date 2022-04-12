import sys 
from adapter import AmepadAdapter
from data_gather import AmepadDataGather
import logging, threading

def run_main(config_file='adapter.yaml', debug_mode=False):
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    
    logger = logging.getLogger()
    lock = threading.Lock()
    adapter = AmepadAdapter(lock, logger, debug_mode)
    adapter.configure(config_file)
    adapter.init_threads()

    data_gather = AmepadDataGather(adapter=adapter,logger=logger)
    data_gather.initialize()
    data_gather.run()

def usage():
    print("That is not proper usage: \n")
    print('Run directly:\n   python main.py run adapter.yaml \n')

if __name__ == '__main__':
    argv_par = sys.argv
    
    if len(argv_par) <= 2:
        usage()
        sys.exit(0)
    else:
        if argv_par[1] == 'debug':
            run_main(argv_par[2], debug_mode=False)

        if argv_par[1] == 'run':
            run_main(argv_par[2], debug_mode=False) 