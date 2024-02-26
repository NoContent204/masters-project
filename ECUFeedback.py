from io import TextIOWrapper
import canCommunication
import can
import time
try:
    bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000)
except OSError:
    print("Please connect to an ECU and set up the CAN interface using ./setup.sh")
    exit(0)
nonUDSTraffic: "dict[int, dict[bytes,int]]" = {} # dictionary mapping can ids to list of dictionaryies mapping the data to an int representing how many times that message has been seen (-1 indicating it was an initial message)
def readDTCInformation():
    resp = canCommunication.sendUDSReq([0x19,0x01,0x05]) # call read DTC info service with subfunction 0x01 (report Number Of DTC By Status Mask)
    # we use a status mask of 0x05 which is a combination of pendingDTC (0x04) status and testFailed (0x01) status

    #bus.send(can.Message(arbitration_id=tx_canID, data=[0x03,0x19,0x01,0x05,0x00,0x00,0x00,0x00] , is_extended_id=False)) 
    #resp = bus.recv(timeout=0.5)
    if (resp):
        #print(resp.data[4])
        return resp.data[4] # print number of DTCs
    else:
        return -1
    
def sortTraffic():
    # Once program has been stopped this code should execute which sorts all recorded traffic by id's that transmit the most messages and then by the frequency of the specific data
    idsANDTraffic = []
    for traffic in nonUDSTraffic.items():
        traffic = list(traffic)
        sortedByFrequency = dict(sorted(traffic[1].items(), key= lambda item: item[1]))
        traffic[1] = sortedByFrequency
        idsANDTraffic.extend(traffic)
    sortedTraffic = {idsANDTraffic[i] : idsANDTraffic[i+1] for i in range (0,len(idsANDTraffic),2)}
    sortedTraffic = dict(sorted(sortedTraffic.items(), key = lambda x: len(x[1])))

    # Also save all the recorded traffic to compare once we're done
    f = open("nonUDSTraffic_new.txt","w")
    for id in nonUDSTraffic:
        f.write(hex(id) + "\n")
        #print(nonUDSTraffic[id].keys())
        for data in nonUDSTraffic[id].keys():
            #print(data)
            if nonUDSTraffic[id][data] != -1:
                f.write(data.hex() + "\n")
        f.write("\n")
    f.close()
    
def recordNonUDSTraffic(initial: bool, logFile: TextIOWrapper):
    bus.set_filters() # reset filters to record all data
    finishT = time.time() + 15 # Record traffic for 10 seconds
    if initial: # dict is empty 
        print("Recording inital traffic...")
        while time.time() < finishT: # get initial traffic
            message = bus.recv(0.5)
            if message == None:
                continue

            id = message.arbitration_id
            if id == canCommunication.RX_CAN_ID or id == canCommunication.TX_CAN_ID: # ignore messages from UDS
                continue
            data = message.data
            if id in nonUDSTraffic:
                nonUDSTraffic[id].update({bytes(data): -1})  
            else:
                nonUDSTraffic.update({id: {bytes(data): -1}})
        f = open("nonUDSTraffic_Initial.txt", "w")
        for id in nonUDSTraffic:
            f.write(hex(id) + "\n")
            for data in nonUDSTraffic[id].keys():
                f.write(data.hex() + "\n")
            f.write("\n")
        f.close()
    else: # get new traffic
        usedInputs = open("usedInputs.txt","r")
        print("Recording new traffic...")
        while True:
            message = bus.recv(0.5) #reader.get_message()#
            if message == None:
                continue

            id = message.arbitration_id
            if id == canCommunication.RX_CAN_ID or id == canCommunication.TX_CAN_ID or id == 0x405 or id == 0x40a: # ignore messages from UDS and id's 0x405 and 0x40a as they seem to always respond to every message
                continue
            data = message.data
            mostRecentInput = usedInputs.readlines()[-1]
            usedInputs.seek(0)
            if not(id in nonUDSTraffic): # id not in traffic 
                logFile.write(hex(id) + " " + bytes(data).hex() + " cause by "+ mostRecentInput+ "\n")
                #logFile.flush()
                #newTraffic.append(message) # ?
                nonUDSTraffic.update({id: {bytes(data): 1}})    
            elif not(bytes(data) in nonUDSTraffic[id]): # id in traffic but not this data
                logFile.write(hex(id) + " " + bytes(data).hex() + " cause by "+ mostRecentInput+ "\n")
                #logFile.flush()
                #newTraffic.append(message) # ?
                nonUDSTraffic[id].update({bytes(data): 1}) # add message info to set of traffic 
            else: # if id AND data seen before
                if (nonUDSTraffic[id][bytes(data)] != -1): # message wasn't part of initial traffic i.e. we don't want to increment number of times seen for initial traffic because it should always be seen
                    nonUDSTraffic[id].update({bytes(data): nonUDSTraffic[id][bytes(data)] + 1}) # increase number of times message has been seen
    #return [newTraffic,nonUDSTraffic]

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
    resp = canCommunication.sendUDSReq(data,timeout=(avgT * timeThresholdMultipler) + 3)
    respT = time.time() - startT
    if respT > avgT * timeThresholdMultipler and resp != None:
        # respT was significantly longer than avgT, and we actually got a response (otherwise all None responses will trigger this)
        return [resp,True,respT] # yes we want to record the data we sent as it caused ECU to take longer to respond
    else:
        return [resp,False,respT]
    