import random
from textwrap import wrap

def bitFlipping(data: "list[int]", iterations: int):
    binarydata: str = ''.join(list(map(lambda x : format(x,'#010b').replace("0b",""),data))) # turn data array into binary string
    
    for x in range(iterations):
        bitIndex = random.randrange(0,len(binarydata))
        if binarydata[bitIndex] == '0':
            binarydata[bitIndex] = '1'
        else:
            binarydata[bitIndex] = '0'

    byteList : "list[str]" = wrap(binarydata,8)
    newdata : list[int] = list(map(lambda binary : int(binary,2), byteList))

    return newdata