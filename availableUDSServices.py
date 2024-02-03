# Script to find which services are avaiable on the UDS implementation we are fuzzing
# import can
# import numpy as np
import canCommunication

# def sendUDSReq(SID, dataFrame):
#    PCI = 0x1 + len(dataFrame) # calculate the length of the data including the SID for the PCI header required by CAN-TP (ISO 15765) (assuming single frame)
#    canData = [PCI,SID] + dataFrame
#    print(canData)
#    canData = list(np.pad(canData,(0,8-len(canData)),'constant',constant_values=0)) # padd data with zeros
#    print(canData)
#    bus.send(can.Message(arbitration_id=tx_canID, data=canData, is_extended_id=False))
#    resp = bus.recv(timeout=6)
#    return resp

SIDs = [
   {
      "SID": 0x10, # Diagnostic session control *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x11, # ECU reset *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x27, # Security Access 
      "hasSubFunction": True ,
   },
   {
      "SID": 0x28, # Communication control *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x29,# Authentication ?
      "hasSubFunction": True ,
   },
   {
      "SID": 0x3e,# Tester Present *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x83, # Access timing parameters *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x84,# Secured data transmission 
      "hasSubFunction": False ,
   },
   {
      "SID": 0x85, # Control DTC Settings *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x86, # Response on Event *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x87, # Link Control *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x22, # Read Data by Identifier
      "hasSubFunction": False ,
   },
   {
      "SID": 0x23, # Read memory by address
      "hasSubFunction": False ,
   },
   {
      "SID": 0x24, # Read Scaling data by identifier
      "hasSubFunction": False ,
   },
   {
      "SID": 0x2a, # Read data by identifier periodic
      "hasSubFunction": False ,
   },
   {
      "SID": 0x2c, # Dynamically defind data identifer *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x2e, # Write data by identifier
      "hasSubFunction": False ,
   },
   {
      "SID": 0x3d, # Write memory by address 
      "hasSubFunction": False ,
   },
   {
      "SID": 0x14, # Clear diagnoistic information
      "hasSubFunction": False ,
   },
   {
      "SID": 0x19, # Read DTC information *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x2f, # Input output control by identifter 
      "hasSubFunction": False ,
   },
   {
      "SID": 0x31, # Routine control *
      "hasSubFunction": True ,
   },
   {
      "SID": 0x34, # Request download
      "hasSubFunction": False ,
   },
   {
      "SID": 0x35, # Request upload
      "hasSubFunction": False ,
   },
   {
      "SID": 0x36, # Transfer data
      "hasSubFunction": False ,
   },
   {
      "SID": 0x37, # Request transfer exit
      "hasSubFunction": False ,
   },
   {
      "SID": 0x38, # Request file transfer 
      "hasSubFunction": False ,
   },
]

# SIDs = {
#    0x10, # Diagnostic session control *
#    #0x11, # ECU reset *
#    0x27, # Security Access *
#    # 0x28, # Communication control *
#    # 0x29, # Authentication ?
#    0x3e, # Tester Present *
#    # 0x83, # Access timing parameters *
#    # 0x84, # Secured data transmission 
#    # 0x85, # Control DTC Settings *
#    # 0x86, # Response on Event *
#    0x87, # Link Control *
#    0x22, # Read Data by Identifier
#    0x23, # Read memory by address
#    # 0x24, # Read Scaling data by identifier
#    # 0x2a, # Read data by identifier periodic
#    # 0x2c, # Dynamically defind data identifer *
#    0x2e, # Write data by identifier
#    0x3d, # Write memory by address 
#    0x14, # Clear diagnoistic information
#    0x19, # Read DTC information *
#    0x2f, # Input output control by identifter 
#    0x31, # Routine control *
#    0x34, # Request download
#    0x35, # Request upload
#    0x36, # Transfer data
#    0x37, # Request transfer exit
#    0x38  # Request file transfer 
# }


#bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000)
#bus.set_filters([{"can_id": 0x72e, "can_mask": 0x72e, "extended": False}]) # set filter to only get responses from the response CAN-ID for UDS (0x72e)
#message = can.Message(arbitration_id=0x7df, data=[0x02,0x3e,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
#print(bus.filters)
#bus.send(message) # send a message to "wake up" the ECU    
#tx_canID = 0x7df

canCommunication.sendWakeUpMessage()
availableServices = list(SIDs)

for service in SIDs:
    SID = service["SID"]
    print("Scanning SID: "+ hex(SID))
    for x in range(5): # try to get a response 5 times to avoid getting None 
      #resp = sendUDSReq(SID, []) # start with blank data
      resp = canCommunication.sendUDSReq([SID] + [])
      if (resp != None and resp.arbitration_id != 0x72e):
         #resp = sendUDSReq(SID, []) # sometimes we get a random message form id 4? so we have to resend 
         resp = canCommunication.sendUDSReq([SID] + [])
      if (resp == None):
         #resp = sendUDSReq(SID, [0x01]) or sendUDSReq(SID,[0x11,0x11,0x11,0x11,0x11,0x11]) # try either a subfunction of 0x01 or all the data being 1's
         resp = canCommunication.sendUDSReq([SID] + [0x01]) or canCommunication.sendUDSReq([SID] + [0x11,0x11,0x11,0x11,0x11,0x11])


      if (resp != None and resp.arbitration_id == 0x72e):
         break # if we got a response then break the loop

    if (resp.data[1] == SID + 0x40): # Postive respose is always the services id + 0x40 e.g. positive reponse for 0x10 is 0x50 
      print("Postive response - Service available")
    elif (resp.data[1] == 0x7f): # Negative response

      # All the response codes (other than 0x11) imply that the service is supported but a specific error has occured, we can still fuzz these services
      if (resp.data[3] == 0x11): # Specific negative response codes
         print("Service not supported")
         #availableServices.remove(SID) 
         availableServices = [service for service in availableServices if not (service['SID'] == SID)]# service is not supported by the BCM so remove the service ID from the list
      elif (resp.data[3] == 0x12):
         print(hex(SID) + " - Sub-function not supported")
      elif (resp.data[3] == 0x13):
         print(hex(SID) + " - Invalid message length/format")
      elif (resp.data[3] == 0x14):
         print(hex(SID) + " - Response too long")
      elif (resp.data[3] == 0x21):
         print(hex(SID) + " - Busy- repeat request")
      elif (resp.data[3] == 0x22):
         print(hex(SID) + " - Conditions not correct")
      elif (resp.data[3] == 0x24):
         print(hex(SID) + " - Request sequence error")
      elif (resp.data[3] == 0x25):
         print(hex(SID) + " - No response from subnet component")
      elif (resp.data[3] == 0x26):
         print(hex(SID) + " - Failure prevents execution of requested action")
      elif (resp.data[3] == 0x31):
         print(hex(SID) + " - Request out of range")
      elif (resp.data[3] == 0x33):
         print(hex(SID) + " - Security access denied")
      elif (resp.data[3] == 0x35):
         print(hex(SID) + " - Invalid key")
      elif (resp.data[3] == 0x36):
         print(hex(SID) + " - Exceeded number of attempts")
      elif (resp.data[3] == 0x37):
         print(hex(SID) + " - Required time delay has not expired")
      elif (resp.data[3] == 0x70):
         print(hex(SID) + " - Upload/dowload not accepted")
      elif (resp.data[3] == 0x71):
         print(hex(SID) + " - Transfer data suspended")
      elif (resp.data[3] == 0x72):
         print(hex(SID) + " - Programming failure")
      elif (resp.data[3] == 0x73):
         print(hex(SID) + " - Wrong block sequence counter")
      elif (resp.data[3] == 0x78):
         print(hex(SID) + " - Request received - repsonse pending")
      elif (resp.data[3] == 0x7e):
         print(hex(SID) + " - Sub funtion not support in active session")
      elif (resp.data[3] == 0x7f):
         print(hex(SID) + " - Service not supported in active session")
      else:
         print("Unexpected issue error code "+ hex(resp.data[3]))
with open('availableServices.log',"a") as log: # Save list of avaiable services to file (to be used by main fuzzer)
   for service in availableServices:
      print(service,file=log)
