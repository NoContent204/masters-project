from boofuzz import * #Session, Target, TCPSocketConnection, RawL3SocketConnection, Request, Bytes, Group, Block, Static, RandomData
import threading
import time
# import ../availableUDSServices
from os.path import exists


def fuzzer():
    # if (not(exists('availableServices.log'))):
    #     availableUDSServices.main()
    f = open('../availableServices.log','r')
    SIDs = list(map(lambda x: int(x.replace("0x",""),16).to_bytes(1,'little'),f.readlines()))    

    s_initialize("Req")
    s_static(0x7df.to_bytes(2,'little'))
    s_static(0x0000.to_bytes(2,'little'))
    s_static(name="dlc",value=0x08.to_bytes(1,'little')),
    s_static(0x000000.to_bytes(3,'little'))

    print(len(SIDs))
    s_group(values=SIDs)

    s_bytes(max_len=7)

    # req = Request("CAN-Request",children=(  
    #     Block("CAN-stuff",children=(
    #         Static("CAN-ID",default_value=0x7df.to_bytes(2,'little')),
    #         Static("flags",default_value=0x0000.to_bytes(2,'little')),
    #         Static("dlc",default_value=0x08.to_bytes(1,'little')),
    #         Static("reserved",default_value=0x000000.to_bytes(3,'little')),
    #         Group("SID", values= SIDs or [0x10.to_bytes(1,'big'),0x11.to_bytes(1,'big'),0x27.to_bytes(1,'big'),0x28.to_bytes(1,'big'),0x29.to_bytes(1,'big'),0x3e.to_bytes(1,'big'),0x83.to_bytes(1,'big'),0x84.to_bytes(1,'big'),0x85.to_bytes(1,'big'),0x86.to_bytes(1,'big'),0x87.to_bytes(1,'big'),0x22.to_bytes(1,'big'),0x24.to_bytes(1,'big'),0x2a.to_bytes(1,'big'),0x2c.to_bytes(1,'big'),0x2e.to_bytes(1,'big'),0x3d.to_bytes(1,'big'),0x14.to_bytes(1,'big'),0x19.to_bytes(1,'big'),0x2f.to_bytes(1,'big'),0x31.to_bytes(1,'big'),0x34.to_bytes(1,'big'),0x35.to_bytes(1,'big'),0x36.to_bytes(1,'big'),0x37.to_bytes(1,'big'),0x38.to_bytes(1,'big')]),

    #     )),
    #     Block("UDS",children=(
    #         Bytes("Data",size=7)
    #     )),
            
    # ))    
    uds_session = Session(target=Target(connection=RawL3SocketConnection(interface="vcan0", ethernet_proto=0x000C)))
    #test_session = Session(target=Target(connection=TCPSocketConnection("127.0.0.1",3000)))

    uds_session.connect(s_get("Req"))
    uds_session.fuzz()

fuzzerThread = threading.Thread(target=fuzzer)
fuzzerThread.daemon = True
fuzzerThread.start()

while True:
    print("Fuzzing...")     
    time.sleep(2)