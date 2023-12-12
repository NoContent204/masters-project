# Simple script to find the UDS canIDs based off ISO 15765-4
import can
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
from udsoncan.exceptions import TimeoutException
import isotp

isotp_params = {
   'stmin' : 32,                          
   'blocksize' : 8,                       
   'wftmax' : 0,                          
   'tx_data_length' : 8,                  
   'tx_data_min_length' : None,           
   'tx_padding' : 0,                      
   'rx_flowcontrol_timeout' : 1000,       
   'rx_consecutive_frame_timeout' : 1000, 
   'squash_stmin_requirement' : False,    
   'max_frame_size' : 4095                
}


bus = can.Bus(interface='socketcan' , channel='can0', bitrate=500000)

message = can.Message(arbitration_id=0x726, data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
bus.send(message) # send a message to "wake up" the ECU    

for canID in range(2015, 2032):
   tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=canID, rxid=0x72e)
   stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)                                                                      
   conn = PythonIsoTpConnection(stack)


   with Client(conn, request_timeout=2) as client:                                    
      try:
         resp = client.tester_present()
         with open('successLog.log',"a") as log:
            msg = str(resp) + " at canID " + hex(canID)
            print(msg, file=log)
      except TimeoutException:
         print("Timeout, no UDS detected for CAN ID " + hex(canID))
