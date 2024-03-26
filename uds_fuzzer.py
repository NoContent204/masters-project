import canCommunication
from testGeneration_Grammar import generateInput
from testGeneration_Mutation import mutateData
from ECUFeedback import readDTCInformation, responseTiming, recordNonUDSTraffic, getAverageResponseTime, sortTraffic
import availableUDSServices

import argparse
import random
import pyradamsa
import threading
from os.path import exists
from os import mkdir
from datetime import datetime
import time

crashFile = "usefulInputs.txt"
SIDs = []
usedInputsFile = "usedInputs.txt"

def randCANframe():
    frame = []
    dlc = random.randint(1,6) # exlcude SID
    SID = random.choice(SIDs)# randomly pick an SID
    frame.append(SID)
    for _ in range(dlc):
        frame.append(random.getrandbits(8)) # generate random data
    return frame

def main():
    if (not(exists('availableServices.log'))):
        availableUDSServices.main()

    f = open('availableServices.log','r')
    global SIDs
    SIDs = list(map(lambda x : int(x,16),f.readlines()))
    f.close()
    radamsa = pyradamsa.Radamsa()
    avgRespT = None
    totalDTCs = 0

    parser = argparse.ArgumentParser(description = "Fuzz the UDS protocol on an ECU")
    # Input generation arguments
    parser.add_argument("-m", "--mutational", action='store_true', help="Enable the use of mutations on inputs") # enable mutations on inputs
    parser.add_argument("-mi", "--mutation-iterations", type=int, default=10, help="Used in conjunction with -m. Sets the number of times an input is mutated (default is 10)") # set number if iterations for mutations
    parser.add_argument("-g", "--grammar", action='store_true', help="Enable the use of inputs produced from a BNF grammar") # enable inputs from grammar
    parser.add_argument("-r", "--radamsa",action="store_true", help="Enable the use of radamsa for fuzz testcase generation") # enable radamsa use

    # Feedback arguments
    parser.add_argument("-d", "--dtc", action="store_true", help="Enable the use of DTC for feedback") # enable feedback via DTC
    parser.add_argument("-ti", "--timing", type=int, help="Enable the use of response timings for feedback, provide threshold multipler for timings. Note: this will slow down the performance as the fuzzer will wait for the timeout before going to the next test case") # enable feedback via repsonse timings
    parser.add_argument("-tr", "--traffic", action="store_true", help="Enable the use of the CAN traffic for feedback") # enable feedback via CAN traffic
    args = parser.parse_args()
    

    if (not(any([args.mutational,args.grammar,args.radamsa]))):
        print("Please provide at least one method for generating inputs (-m, -g or -r). Use -h or --help for help")
        exit(0)

    if (not(any([args.dtc,args.timing,args.traffic]))):
        print("Please provide at least one method for feedback (-d, -ti or -tr). Use -h or --help for help")
        exit(0)
    if (args.mutational and args.radamsa):
        print("Please use either the muatational setting OR the radamsa setting or neither")
        exit(0)
    if (args.timing):
        getAverageResponseTime(5)
    
    dirName = "results/"+datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    mkdir(dirName)


    usedInputs = open(dirName+"/"+usedInputsFile,'a+')
    usedInputs.write(bytes([0]).hex()+"\n")
    usedInputs.seek(0)


    logFile = open(dirName+"/"+crashFile,'a+')
    if (args.traffic):
        canCommunication.sendWakeUpMessage()
        recordNonUDSTraffic(True, None, dirName)
        thread = threading.Thread(target=recordNonUDSTraffic, args=(False,logFile,dirName,))
        thread.daemon = True
        canCommunication.sendWakeUpMessage()
        thread.start() # Start the recording of traffic asynchronously
    else:
        canCommunication.sendWakeUpMessage()
    
    canCommunication.extendedSession() # put us in extended session
    startTime = time.time()
    while True:
        try:
            if (args.grammar):
                initialData = generateInput()
            else:
                initialData = randCANframe()
            

            data = [0]
            currentInputs = list(map(lambda x: x.replace("\n",""), usedInputs.readlines()))
            while bytes(data).hex() in currentInputs:
                if (args.mutational):
                    data = mutateData(initialData, args.mutation_iterations)            
                elif (args.radamsa):
                    data = [initialData[0]] + list(radamsa.fuzz(initialData[1:],max_mut=6)) # ignore SID when using radamsa to mutate
                else:
                    data = initialData
            print("Fuzzing with "+bytes(data).hex() + "\n")
            usedInputs.seek(0,2) # go to end of file to write new input
            usedInputs.write(bytes(data).hex() + "\n") # add data to list of used inputs
            usedInputs.seek(0)  # go to start of file

            
            if (args.timing):
                respData = responseTiming(avgT=avgRespT, data=data, timeThresholdMultipler=args.timing)
                resp = respData[0]
                if (respData[1]): # response took long enough to trigger threshold
                    logFile.write(bytes(data).hex() + " casued ECU to take " + str(respData[1]) + " seconds to respond\n")
            else:
                resp = canCommunication.sendUDSReq(data)
            if (resp != None):
                if resp.data[1] != 0x7f:
                    logFile.write(bytes(data).hex() + " caused positive response: "+resp.data[2:].hex()+"\n")
                else:
                    if (resp.data[3] == 0x7f):
                        canCommunication.extendedSession() # if "Service unavailable in current session" make sure we're in an extended session
                    if (resp.data[3] != 0x13): # ignore errors that are about invalid lengths/formats
                        logFile.write(bytes(data).hex() + " caused negaitve response. NRC: "+hex(resp.data[3])+"\n")
            
            if (args.dtc):
                dtcs = readDTCInformation()
                if (dtcs != -1): # make sure we got something
                    if (dtcs > totalDTCs): # test caused DTC(s)
                        logFile.write(bytes(data).hex() + " caused " + str(dtcs - totalDTCs) + " DTC(s)\n")
                    totalDTCs = dtcs

        except KeyboardInterrupt:
            timeRunning = time.time() - startTime
            usedInputs.seek(0)
            logFile.seek(0)
            print("Fuzzer ran for "+str(timeRunning)+"s ("+str(timeRunning/60)+" mins)")
            print("Fuzzing ended by user...\nFuzzer produced: "+str(len(usedInputs.readlines()))+ " inputs")
            print("Fuzzer found "+str(len(logFile.readlines()))+ " interesting inputs   ")
            logFile.close()
            usedInputs.close()
            sortTraffic(dirName)
            exit(0)

main()