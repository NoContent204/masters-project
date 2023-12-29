# Simple script to find the UDS canIDs based off ISO 15765-4
import can

SIDs = {
   0x10, # Diagnostic session control
   0x11, # ECU reset
   0x27, # Security Access
   0x28, # Communication control
   0x29, # Authentication
   0x3e, # Tester Present
   0x83, # Access timing parameters
   0x84, # Secured data transmission
   0x85, # Control DTC Settings
   0x86, # Response on Event
   0x87, # Link Control
   0x22, # Read Data by Identifier
   0x23, # Read memory by address
   0x24, # Read Scaling data by identifier
   0x2a, # Read data by identifier periodic
   0x2c, # Dynamically defind data identifer
   0x2e, # Write data by identifier
   0x3d, # Write memory by address
   0x14, # Clear diagnoistic information
   0x19, # Read DTC information
   0x2f, # Input output control by identifter 
   0x31, # Routine control 
   0x34, # Request download
   0x35, # Request upload
   0x36, # Transfer data
   0x37, # Request transfer exit
   0x38  # Request file transfer 
}


bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000)
bus.set_filters([{"can_id": 0x72e, "can_mask": 0xff, "extended": False}])

message = can.Message(arbitration_id=0x7df, data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
print(bus.filters)
bus.send(message) # send a message to "wake up" the ECU    
tx_canID = 0x7df
# rx_canID = 0x72e
# tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=canID, rxid=0x72e)
# stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)                                                                      
# conn = PythonIsoTpConnection(stack)

availableServices = list(SIDs)
# bus.send(can.Message(arbitration_id=tx_canID, data=[0x02,0x10,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False))
# resp = bus.recv()
# print(resp.data[1])
# print(hex(resp.arbitration_id))


for SID in SIDs:
    print(hex(SID))
    bus.send(can.Message(arbitration_id=tx_canID, data=[0x02,SID,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False))
    resp = bus.recv(timeout=2)
    if (resp.data[1] == SID + 0x40): # Postive respose is always the services id + 0x40 e.g. positive reponse for 0x10 is 0x50 
      print("Postive response - Service available")
    elif (resp.data[1] == 0x7f): # Negative response

      # All the response codes (other than 0x11) imply that the service is supported but a specific error has occured, we can still fuzz these services
      if (resp.data[3] == 0x11): # Specific negative response codes
         print("Service not supported")
         availableServices.remove(SID) # service is not supported by the BCM so remove the service ID from the list
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
         print(hex(SID) + " - Failure prevents eecution of requested action")
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
   for SID in availableServices:
      print(hex(SID),file=log)
