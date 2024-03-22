# A simple python script to set up inital communication with the BCM
import can

channel = "can0"
Bus = can.Bus(interface='socketcan', channel='can0', bitrate = 500000)

# Create and send a message that we know what will happen with the traffic based off the previous report
message = can.Message(arbitration_id=0xc0, data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
Bus.send(message, timeout=0)
resp = Bus.recv()
print(resp)


#initalMessage = can.Message(arbitration_id=0x280, data=[0x00,0x00,0x00,0x22,0x00,0x00,0x00,0x00], is_extended_id=False)
#Bus.send_periodic(initalMessage,period=0.01)