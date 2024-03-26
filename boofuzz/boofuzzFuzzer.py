from boofuzz import *
import threading
import time
from os.path import exists


def fuzzer():

    f = open('../availableServices.log','r')
    SIDs = list(map(lambda x: int(x.replace("0x",""),16).to_bytes(1,'little'),f.readlines()))    

    s_initialize("Req")
    s_static(0x7df.to_bytes(2,'little'))
    s_static(0x0000.to_bytes(2,'little'))
    s_static(name="dlc",value=0x08.to_bytes(1,'little')),
    s_static(0x000000.to_bytes(3,'little'))

    print(len(SIDs))
    s_group(values=SIDs)

    s_bytes(size=7)
  
    uds_session = Session(target=Target(connection=RawL3SocketConnection(interface="can0", ethernet_proto=0x000C)))

    uds_session.connect(s_get("Req"))
    uds_session.fuzz()

fuzzerThread = threading.Thread(target=fuzzer)
fuzzerThread.daemon = True
fuzzerThread.start()

while True:
    print("Fuzzing...")     
    time.sleep(2)