# This file implements a simple BNF grammar for the structure of single frame UDS requests using a dictionary that maps nonterminal symbols to their corresponding expansions
import re
from textwrap import wrap
import numpy
UDS_Grammar: "dict[str, list[str]]" =  {
    "<start>": ["<udsReq>"],
    "<udsReq>": ["<SID><subfunction><data-2>", "<SID><data-1>"],
    "<SID>": ["10","11","27","28","29","3e","83","84","85","86","87","22","24","2a","2c","2e","3d","14","19","2f","31","34","35","36","37","38"],
    "<subfunction>": ["<hex-2><hex>"], # subfunction byte limited to ranging from 0x00 to 0x7f since 0x80 onwards have the suppress positive result bit set
    "<data-1>": ["<byte>"*6], # 2 separate data defs based on whether a byte has been used for the subfunction
    "<data-2>": ["<byte><byte><byte><byte><byte>"],
    "<byte>": ["<hex><hex>"],
    "<hex>": ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"],
    "<hex-2>" : ["0","1","2","3","4","5","6","7"]
}

UDS_Grammar2: "dict[str,dict[str,list[any]]]" = { # grammar using probabilities, allows for varying length of the data
    "<start>": {"options":["<udsReq>"],"probs":[1]}, # only one option
    "<udsReq>": {"options":["<SID><subfunction><data>", "<SID><data>"],"probs":[0.5,0.5]}, # equal chances
    "<SID>": {"options":["10","11","27","28","29","3e","83","84","85","86","87","22","24","2a","2c","2e","3d","14","19","2f","31","34","35","36","37","38"],"probs":[0.038461538 for x in range(26)]}, # currently equal chances, will be updated based on results from service scanner
    "<subfunction>": {"options":["<hex-2><hex>"],"probs":[1]},
    "<data>": {"options":["<byte><byte>", "<data><byte>"], "probs":[0.5,0.5]},
    "<byte>": {"options":["<hex><hex>"],"probs": [1]}, # only 1 option
    "<hex>": {"options":["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"],"probs":[0.0625 for x in range(16)]}, # equal chances
    "<hex-2>" : {"options":["0","1","2","3","4","5","6","7"],"probs":[0.125 for x in range(8)]} #equal chances
    }
startTerm = "<start>"
nonTerminalPattern = '<[^<> ]+>'


def generateInput():
    currentTerm = startTerm

    while(len(re.findall(nonTerminalPattern,currentTerm)) !=0): # while there are still non terminal symbols to expand
        # print(re.findall(nonTerminalPattern,currentTerm))
        # print(currentTerm)

        expandingSymbol: str = re.findall(nonTerminalPattern,currentTerm)[0] # get first non terminal symbol
        expansionOptions: "list[str]" = UDS_Grammar2[expandingSymbol] # get list of expanding options for that symbol
        #print(expansionOptions)

        probabilites = expansionOptions["probs"]
        expansionList = expansionOptions["options"]
        chosenExpansion = numpy.random.choice(expansionList,p=probabilites) # choose an expansion based off the probabilites

        #print(chosenExpansion)

        # print("chosen = "+chosenExpansion)

        #print(expandingSymbol + " ----> "+ chosenExpansion)
        currentTerm = currentTerm.replace(expandingSymbol,chosenExpansion,1) # replace the non terminal symbol with the chosen expansion
        

    byteList : "list[str]" = wrap(currentTerm,2) # split generated string into list of hex strings for each byte
    generatedInput : list[int] = list(map(lambda hex: int(hex,16),byteList))
    if (len(generatedInput) > 7):
        return generatedInput[:7] # return only 7 bytes
    else:
        return generatedInput

y = []
#print(generateInput())
# for x in range(1000):
#     y.append(len(generateInput()))
# print("Average len = "+str(sum(y)/len(y)))
# print("Max input len = "+str(max(y)))
# print("Min input len = "+str(min(y)))