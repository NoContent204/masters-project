import canCommunication
import can
from can import Message
import time
try:
    bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000)
except OSError:
    print("Please connect to an ECU and set up the CAN interface using ./setup.sh")
    exit(0)
nonUDSTraffic: "dict[int, dict[bytearray,int]]" = {} # dictionary mapping can ids to list of dictionaryies mapping the data to an int representing how many times that message has been seen (-1 indicating it was an initial message)
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
    
def recordNonUDSTraffic(initial: bool):
    bus.set_filters() # reset filters to record all data
    finishT = time.time() + 10 # Record traffic for 10 seconds
    newTraffic: "list[Message]"= []
    if initial: # dict is empty
        while time.time() < finishT: # get initial traffic
            message = bus.recv(0.5)
            if message == None:
                continue

            id = message.arbitration_id
            if id == canCommunication.RX_CAN_ID: # ignore messages from UDS
                continue
            data = message.data
            if id in nonUDSTraffic:
                nonUDSTraffic[id].append({data: -1})  
            else:
                nonUDSTraffic[id] = [{data: -1}]
        f = open("nonUDSTraffic_Initial.txt", "w")
        for id in nonUDSTraffic:
            f.write(hex(id) + "\n")
            for data in nonUDSTraffic[id]:
                f.write(bytes(data).hex() + "\n")
            f.write("\n")
        f.close()
    else: # get new traffic
        f = open("nonUDSTraffic_new.txt","a")
        while time.time() < finishT:
            message = bus.recv(0.5)
            if message == None:
                continue

            id = message.arbitration_id
            if id == canCommunication.RX_CAN_ID: # ignore messages from UDS
                continue
            data = message.data
            if not(id in nonUDSTraffic): # id not in traffic 
                f.write(hex(id) + " " + bytes(data).hex() + "\n")
                newTraffic.append(message) # ?
                nonUDSTraffic.update({id: {data: 1}})    
            elif not(data in nonUDSTraffic[id]): # id in traffic but not this data
                f.write(hex(id) + " " + bytes(data).hex() + "\n")
                newTraffic.append(message) # ?
                nonUDSTraffic[id].update({data: 1}) # add message info to set of traffic 
            else: # if id AND data seen before
                if (nonUDSTraffic[id][data] != -1): # message wasn't part of initial traffic i.e. we don't want to increment number of times seen for initial traffic because it should always be seen
                    nonUDSTraffic[id].update({data: nonUDSTraffic[id][data] + 1}) # increase number of times message has been seen
        f.close()
    return [newTraffic,nonUDSTraffic]

def getAverageResponseTime(n: int):
    testerPresentFrame = [0x3e,0x00]
    totalT = 0
    for _ in range(n):
        startT =  time.time()
        _ = canCommunication.sendUDSReq(testerPresentFrame)
        respT = time.time() - startT
        totalT += respT
    avgT = totalT / n
    return avgT

def responseTiming(avgT: float, data: "list[int]", timeThresholdMultipler: int): # pass avgT (for comparison), data (to send) and timeThresholdMultipler (mulitpler for avgT to compare respT)
    startT = time.time()
    _ = canCommunication.sendUDSReq(data)
    respT = time.time() - startT
    if respT > avgT * timeThresholdMultipler:
        # respT was significantly longer than avgT
        return [True,respT] # yes we want to record the data we sent as it caused ECU to take longer to respond
    else:
        return [False,respT]
    