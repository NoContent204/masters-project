import random
from textwrap import wrap
from testGeneration_Grammar import generateInput

def bitFlipping(data: "list[int]", iterations: int):
    binarydata: str = ''.join(list(map(lambda x : format(x,'#010b').replace("0b",""),data))) # turn data array into binary string
    for x in range(iterations):
        bitIndex = random.randrange(8,len(binarydata)) # ignore the first byte (SID)
        if binarydata[bitIndex] == '0':
            binarydata = binarydata[:bitIndex] + '1' + binarydata[bitIndex + 1:]
        else:
            binarydata = binarydata[:bitIndex] + '0' + binarydata[bitIndex + 1:]

    byteList : "list[str]" = wrap(binarydata,8)
    newdata : list[int] = list(map(lambda binary : int(binary,2), byteList))

    return newdata


def logicalAND(a: int, b: int ):
    return a & b
def logicalOR(a: int, b: int):
    return a | b
def logicalXOR(a: int, b: int):
    return a ^ b
def logicalNOT(a: int, _):
    return abs(~a)

def logicalMutations(data: "list[int]", iterations: int):
    # & and, | or , ^ xor, ~ not
    for x in range(iterations):
        logicalFunc = random.choice([logicalAND,logicalOR,logicalXOR,logicalNOT])
        byteIndex = random.randrange(1, len(data)) # ignore the first byte (SID)
        randByte = random.getrandbits(8)
        data[byteIndex] = logicalFunc(data[byteIndex], randByte)

    return data

def byteShift(data: "list[int]", iterations: int):
    for x in range(iterations):
        shift = random.randint(0,255)
        byteIndex = random.randrange(1, len(data)) # ignore the first byte (SID)
        lORr = random.randint(0,1)
        if lORr == 1:
            data[byteIndex] = (data[byteIndex] >> shift) % 255
        else:
            data[byteIndex] = (data[byteIndex] << shift) % 255

    return data