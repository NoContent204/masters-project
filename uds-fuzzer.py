import canCommunication
from testGeneration_Grammar import generateInput
from testGeneration_Mutation import bitFlipping, byteShift, logicalMutations
from ECUFeedback import readDTCInformation, responseTiming, recordNonUDSTraffic, getAverageResponseTime
import argparse

def main():
    testGenerationMethods = []
    feedbackMethods = []
    avgRespT = None

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
        feedbackMethods.append(recordNonUDSTraffic)

    if (len(feedbackMethods) == 0): # no feedback methods given
        print("Please provide at least one method for feedback (-d, -ti or -tr). Use -h or --help for help")
        exit(0)

main()