# This file implements a simple BNF grammar for the structure of UDS requests using a dictionary that maps nonterminal symbols to their corresponding expansions

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