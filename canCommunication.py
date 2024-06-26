# File for functions relating to communicating via the CAN bus
import can
import numpy as np

TX_CAN_ID = 0x7df
RX_CAN_ID = 0x72e
try:
    bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000) # set up can bus communication
    bus.set_filters([{"can_id": RX_CAN_ID, "can_mask": RX_CAN_ID, "extended": False}]) # set filter to only get responses from the response CAN-ID for UDS
except OSError:
    print("Please connect to an ECU and set up the CAN interface using ./setup.sh")
    exit(0)


def sendUDSReq(dataFrame, timeout=0.2): # SID included within dataFrame array
    PCI = [len(dataFrame)] # PCI (CAN-TP) header includes length of the data 
    canData: list[int] = PCI + dataFrame # combine the two into a single array
    canData = list(np.pad(canData,(0,8-len(canData)),'constant',constant_values=0)) # padd data with zeros
    bus.send(can.Message(arbitration_id=TX_CAN_ID, data=canData, is_extended_id=False)) # send data
    resp = bus.recv(timeout) # get response
    return resp

def extendedSession():
    resp = None
    while (resp == None): # repeat sending the message until we get a response i.e we have changed sessions 
        bus.send(can.Message(arbitration_id=TX_CAN_ID, data=[0x02,0x10,0x03,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)) # switch to extended diagnostic control session
        resp = bus.recv(0.5)


def sendWakeUpMessage(): # function to send a wake up message to the ECU (Tester present) to make sure ECU will respond to fuzzing messages
    resp = None
    while (resp == None): # repeat sending the message until we get a response i.e the ECU is no longer idle 
        bus.send(can.Message(arbitration_id=TX_CAN_ID, data=[0x02,0x3e,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False))
        resp = bus.recv(0.5)