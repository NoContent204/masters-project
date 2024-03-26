import random
from textwrap import wrap

def mutateData(data: "list[int]", iterations: int):
    for _ in range(iterations):
        mutation = random.choice([bitFlipping,logicalMutations,byteShift,byteDeletion,byteAddition]) # pick a random mutation function
        data = mutation(data, 1)
    return data         

def bitFlipping(data: "list[int]", iterations: int):
    if (len(data) != 1):
        binarydata: str = ''.join(list(map(lambda x : format(x,'#010b').replace("0b",""),data))) # turn data array into binary string
        for x in range(iterations):
            bitIndex = random.randrange(8,len(binarydata)) # ignore the first byte (SID)
            if binarydata[bitIndex] == '0':
                binarydata = binarydata[:bitIndex] + '1' + binarydata[bitIndex + 1:]
            else:
                binarydata = binarydata[:bitIndex] + '0' + binarydata[bitIndex + 1:]

        byteList : "list[str]" = wrap(binarydata,8)
        newdata : list[int] = list(map(lambda binary : int(binary,2) % 256, byteList)) # make sure all data is between 0 and 255

        return newdata
    else:
        return data


def logicalAND(a: int, b: int ):
    return a & b
def logicalOR(a: int, b: int):
    return a | b
def logicalXOR(a: int, b: int):
    return a ^ b
def logicalNOT(a: int, _):
    return abs(~a)

def logicalMutations(data: "list[int]", iterations: int):
    for x in range(iterations):
        logicalFunc = random.choice([logicalAND,logicalOR,logicalXOR,logicalNOT])
        if (len(data) > 2):
            byteIndex = random.randrange(1, len(data)) # ignore the first byte (SID)
            randByte = random.getrandbits(8)
            data[byteIndex] = logicalFunc(data[byteIndex], randByte) % 256

    return data

def byteShift(data: "list[int]", iterations: int):
    for x in range(iterations):
        shift = random.randint(0,255)
        if (len(data) != 1):
            byteIndex = random.randrange(1, len(data)) # ignore the first byte (SID)
            lORr = random.randint(0,1)
            if lORr == 1:
                data[byteIndex] = (data[byteIndex] >> shift) % 256
            else:
                data[byteIndex] = (data[byteIndex] << shift) % 256

    return data

def byteDeletion(data: "list[int]", iterations: int):
    for _ in range(iterations):
        if (len(data) == 1):
            return data # can't delete anymore bytes
        else:
            index = random.randrange(1,len(data)) # don't delete SID
            del data[index]
    return data

def byteAddition(data: "list[int]", iterations: int):
    for _ in range(iterations):
        if (len(data) == 7):
            return data # can't add anymore data (7 bytes is max length of data because CAN frame is 8 bytes (7 bytes of data + PCI byte))
        else:
            index = random.randrange(1,len(data) + 1) # don't insert at start i.e. don't override SID
            newByte = random.getrandbits(8)
            data.insert(index,newByte)
    return data
