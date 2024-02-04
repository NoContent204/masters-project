import canCommunication
import can
from can import Message
import time
bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000)
nonUDSTraffic: "dict[int, list[bytearray]]" = {}
newTraffic: "list[Message]"= []
def readDTCInformation():
    resp = canCommunication.sendUDSReq([0x19,0x01,0x05]) # call read DTC info service with subfunction 0x01 (report Number Of DTC By Status Mask)
    # we use a status mask of 0x05 which is a combination of pendingDTC (0x04) status and testFailed (0x01) status

    #bus.send(can.Message(arbitration_id=tx_canID, data=[0x03,0x19,0x01,0x05,0x00,0x00,0x00,0x00] , is_extended_id=False)) 
    #resp = bus.recv(timeout=0.5)
    if (resp):
        print(resp.data[4])
        return resp.data[4] # print number of DTCs
    else:
        return -1
    
def recordNonUDSTraffic():
    bus.set_filters() # reset filters to record all data
    finishT = time.time() + 5 # Record traffic for 5 seconds
    if nonUDSTraffic: # dict is empty
        while time.time() < finishT: # get initial traffic
            message = bus.recv(0.5)
            if message == None:
                continue

            id = message.arbitration_id
            if id == canCommunication.RX_CAN_ID: # ignore messages from UDS
                continue
            data = message.data
            if id in nonUDSTraffic:
                nonUDSTraffic[id].append(data)  
            else:
                nonUDSTraffic[id] = [data]
    else: # get new traffic
        while time.time() < finishT:
            message = bus.recv(0.5)
            if message == None:
                continue

            id = message.arbitration_id
            if id == canCommunication.RX_CAN_ID: # ignore messages from UDS
                continue
            data = message.data
            if not(id in nonUDSTraffic) or not(data in nonUDSTraffic[id]): # either traffic from a new canID or data that hasn't been sent before 
                newTraffic.append(message) # record the new message received
                nonUDSTraffic[id].append(data) # add message info to set of traffic 
    