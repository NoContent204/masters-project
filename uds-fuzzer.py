import canCommunication
from testGeneration_Grammar import generateInput
from testGeneration_Mutation import bitFlipping, byteShift, logicalMutations
from ECUFeedback import readDTCInformation, responseTiming, recordNonUDSTraffic, getAverageResponseTime
import availableUDSServices
import argparse
import random
import pyradamsa
from os.path import exists

crashFile = "crashes.txt"
SIDs = []

def randCANframe():
    frame = []
    dlc = random.randint(1,6) # exlcude SID
    SID = random.choice(SIDs)#["SID"] # randomly pick an SID
    frame.append(SID)
    for _ in range(dlc):
        frame.append(random.getrandbits(8)) # generate random data
    return frame

def main():
    if (not(exists('availableServices.log'))):
        availableUDSServices.main()

    f = open('availableServices.log','r')
    SIDs = list(map(lambda x : int(x,16),f.readlines()))
    f.close()
    radamsa = pyradamsa.Radamsa()
    testGenerationMethods = []
    feedbackMethods = []
    avgRespT = None
    totalDTCs = 0
    usedInputs = {[]: 1}

    parser = argparse.ArgumentParser(description = "Fuzz the UDS protocol on an ECU")
    # Input generation arguments
    parser.add_argument("-m", "--mutational", action='store_true', help="Enable the use of mutations on inputs") # enable mutations on inputs
    parser.add_argument("-mi", "--mutation-iterations", type=int, default=10, help=" Used in conjunction with -m. Sets the number of times an input is mutated (default is 10)") # set number if iterations for mutations
    parser.add_argument("-g", "--grammar", action='store_true', help="Enable the use of inputs produced from a BNF grammar") # enable inputs from grammar
    parser.add_argument("-r", "--radamsa",action="store_true", help="Enable the use of radamsa for fuzz testcase generation") # enable radamsa use

    # Feedback arguments
    parser.add_argument("-d", "--dtc", action="store_true", help="Enable the use of DTC for feedback") # enable feedback via DTC
    parser.add_argument("-ti", "--timing", type=int, help="Enable the use of response timings for feedback, provide threshold multipler for timings. Note: this will slow down the performance as the fuzzer will wait for the timeout before going to the next test case") # enable feedback via repsonse timings
    parser.add_argument("-tr", "--traffic", action="store_true", help="Enable the use of the CAN traffic for feedback") # enable feedback via CAN traffic
    args = parser.parse_args()
    
    if (args.mutational and args.radamsa):
        print("Please use either the muatational setting OR the radamsa setting or neither")
        exit(0)
    if (args.radamsa):
        testGenerationMethods.append(radamsa.fuzz)
    if (args.mutational):
        testGenerationMethods.append(byteShift)
        testGenerationMethods.append(bitFlipping)
        testGenerationMethods.append(logicalMutations)
    if (args.grammar):
        testGenerationMethods.append(generateInput)
    if (len(testGenerationMethods) == 0): # no test generation methods given
        print("Please provide at least one method for generating inputs (-m, -g or -r). Use -h or --help for help")
        exit(0)
    if (args.dtc):
        feedbackMethods.append(readDTCInformation)
    if (args.timing):
        avgRespT = getAverageResponseTime(5)
        feedbackMethods.append(responseTiming)
    if (args.traffic):
        recordNonUDSTraffic(True)
        feedbackMethods.append(recordNonUDSTraffic)

    if (len(feedbackMethods) == 0): # no feedback methods given
        print("Please provide at least one method for feedback (-d, -ti or -tr). Use -h or --help for help")
        exit(0)

    logFile = open(crashFile,'a')

    while True:
        try:
            if (generateInput in testGenerationMethods):
                initialData = generateInput()
            else:
                initialData = randCANframe()
            

            mutationMethods = [method for method in testGenerationMethods if method != generateInput]
            data = []
            while data in usedInputs:
                if (args.mutational):
                    mutate = random.choice(mutationMethods) # pick a random mutation function
                    data = mutate(initialData, args.mutation_iterations)            
                elif (args.radamsa):
                    mutate = mutationMethods[0] # if radamsa is set there will only be one muation method
                    data = mutate(initialData,max_mut=7)
                else:
                    data = initialData
            usedInputs[data] = 1 # add data to list of used inputs
            
            if (args.timing):
                respData = responseTiming(avgT=avgRespT, data=data, timeThresholdMultipler=args.timing)
                resp = respData[0]
                if (respData[1]): # response took long enough to trigger threshold
                    logFile.write(bytes(data).hex() + " casued ECU to take " + str(respData[1]) + " seconds to respond\n")
                    #print(bytes(data).hex() + " casued ECU to take " + str(respData[1]) + "seconds to respond\n") # CHANGE TO WRITE TO FILE LATER (with reason)
            else:
                resp = canCommunication.sendUDSReq(data)
            
            if (resp == None):
                logFile.write(bytes(data).hex() + " caused a None reponse (likely due to timeout from no response)\n")
                #print(bytes(data).hex() + " caused a None reponse (likely due to timeout from no response)\n") # CHANGE TO WRITE TO FILE LATER (with reason)
            
            if (args.dtc):
                dtcs = readDTCInformation()
                if (dtcs != -1): # make sure we got something
                    if (dtcs > totalDTCs): # test caused DTC(s)
                        logFile.write(bytes(data).hex() + " caused " + str(dtcs - totalDTCs) + " DTC(s)\n")
                        #print(bytes(data).hex() + " caused " + str(dtcs - totalDTCs) + " DTC(s)\n") # CHANGE TO WRITE TO FILE LATER (with reason)
                    totalDTCs = dtcs
            if (args.traffic):
                Traffic = recordNonUDSTraffic(False)
                if (bool(Traffic[0])): # test caused new CAN traffic
                    logFile.write(bytes(data).hex() + " caused new CAN traffic to occur: " + str(Traffic[0]) +"\n")
                    #print(bytes(data).hex() + " caused new CAN traffic to occur: " + str(Traffic[0]) +"\n") # CHANGE TO WRITE TO FILE LATER (with reason) # place holder 
        except KeyboardInterrupt:
            logFile.close()
            exit(0)


main()