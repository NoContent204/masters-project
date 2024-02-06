import canCommunication
from testGeneration_Grammar import generateInput
from testGeneration_Mutation import bitFlipping, byteShift, logicalMutations
from ECUFeedback import readDTCInformation, responseTiming, recordNonUDSTraffic, getAverageResponseTime
from availableUDSServices import SIDs
import argparse
import random

def randCANframe():
    frame = []
    dlc = random.randint(1,6) # exlcude SID
    SID = random.choice(SIDs)["SID"] # randomly pick an SID
    frame.append(SID)
    for _ in range(dlc):
        frame.append(random.getrandbits(8)) # generate random data
    return frame

def main():
    testGenerationMethods = []
    feedbackMethods = []
    avgRespT = None
    totalDTCs = 0

    parser = argparse.ArgumentParser(description = "Fuzz the UDS protocol on an ECU")
    parser.add_argument("-m", "--mutational", action='store_true', help="Enable the use of mutations on inputs") # enable mutations on inputs
    parser.add_argument("-mi", "--mutation-iterations", type=int, default=10, help="Set number of times an input is mutated (default is 10)") # set number if iterations for mutations
    parser.add_argument("-g", "--grammar", action='store_true', help="Enable the use of inputs produced from a BNF grammar") # enable inputs from grammar
    parser.add_argument("-d", "--dtc", action="store_true", help="Enable the use of DTC for feedback") # enable feedback via DTC
    parser.add_argument("-ti", "--timing", type=int, help="Enable the use of response timings for feedback, provide threshold multipler for timings") # enable feedback via repsonse timings
    parser.add_argument("-tr", "--traffic", action="store_true", help="Enable the use of the CAN traffic for feedback") # enable feedback via CAN traffic
    args = parser.parse_args()
    
    if (args.mutational):
        testGenerationMethods.append(byteShift)
        testGenerationMethods.append(bitFlipping)
        testGenerationMethods.append(logicalMutations)
    if (args.grammar):
        testGenerationMethods.append(generateInput)
    if (len(testGenerationMethods) == 0): # no test generation methods given
        print("Please provide at least one method for generating inputs (-m or -g). Use -h or --help for help")
        exit(0)
    if (args.dtc):
        feedbackMethods.append(readDTCInformation)
    if (args.timing):
        avgRespT = getAverageResponseTime()
        feedbackMethods.append(responseTiming)
    if (args.traffic):
        recordNonUDSTraffic(True)
        feedbackMethods.append(recordNonUDSTraffic)

    if (len(feedbackMethods) == 0): # no feedback methods given
        print("Please provide at least one method for feedback (-d, -ti or -tr). Use -h or --help for help")
        exit(0)

    while True:
        if (generateInput in testGenerationMethods):
            initialData = generateInput()
        else:
            initialData = randCANframe()
        
        if (args.mutational):
            mutate = random.choice([method for method in testGenerationMethods if method != generateInput]) # pick a random mutation function
            data = mutate(initialData, args.mutation_iterations)            
        else:
            data = initialData
        
        if (args.timing):
            x = responseTiming(avgT=avgRespT, data=data, timeThresholdMultipler=args.timing)
            if (x[0]): # response took long enough to trigger threshold
                print(str(data) + " casued ECU to take " + str(x[1]) + "seconds to respond") # CHANGE TO WRITE TO FILE LATER (with reason)
        else:
            resp = canCommunication.sendUDSReq(data)
        if (args.dtc):
            dtcs = readDTCInformation()
            if (dtcs > totalDTCs): # test caused DTC(s)
                print(str(data) + " caused " + str(dtcs - totalDTCs) + "DTC(s)") # CHANGE TO WRITE TO FILE LATER (with reason)
            totalDTCs = dtcs
        if (args.traffic):
            newTraffic = recordNonUDSTraffic(False)
            if (bool(newTraffic)): # test caused new CAN traffic
                print(str(data) + " caused new CAN traffic to occur: " + str(newTraffic)) # CHANGE TO WRITE TO FILE LATER (with reason)

main()