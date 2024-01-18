# This file implements a simple BNF grammar for the structure of single frame UDS requests using a dictionary that maps nonterminal symbols to their corresponding expansions
import re
import random
from textwrap import wrap
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
startTerm = "<start>"
nonTerminalPattern = '<[^<> ]+>'


def generateInput():
    currentTerm = startTerm

    while(len(re.findall(nonTerminalPattern,currentTerm)) !=0): # while there are still non terminal symbols to expand
        # print(re.findall(nonTerminalPattern,currentTerm))
        expandingSymbol: str = re.findall(nonTerminalPattern,currentTerm)[0] # get first non terminal symbol
        expansionList: "list[str]" = UDS_Grammar[expandingSymbol] # get list of expanding options for that symbol
        chosenExpansion : str = random.choice(expansionList) # pick one of the options randomly
        # print(expandingSymbol + " ----> "+ chosenExpansion)
        currentTerm = currentTerm.replace(expandingSymbol,chosenExpansion,1) # replace the non terminal symbol with the chosen expansion

    byteList : "list[str]" = wrap(currentTerm,2) # split generated string into list of hex strings for each byte
    generatedInput : list[int] = list(map(lambda hex: int(hex,16),byteList))

    return generatedInput

print(generateInput())