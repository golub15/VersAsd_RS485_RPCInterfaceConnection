

def crc8540(pcBlock):
    lb = len(pcBlock)
    b = 0
    num = 0
    while 1:
        num2 = lb
        lb = num2 - 1
        if num2 <= 0:
            break
        num3 = num
        num = num3 + 1
        b2 = pcBlock[num3]
        for i in range(8, 0, -1):
            b3 = (b2 ^ b) & 1
            b = (b >> 1)
            b2 = (b2 >> 1)
            if b3 != 0:
                b ^= (24 >> 1 | 128)
    return b
def crcok(data):
    c1 = crc8540(data[:len(data) - 1])
    print('data len ->', len(data))
    print('crc data ->', c1)
    cd = data[-1]
    if cd == c1:
        return True
    else:
        return False
def make_packet(adr, pdu):
    a = adr + pdu
    crc = crc8540(a)
    a += bytes([crc])
    return a
def get_rus(arr):
    rus_word = ''
    for i in arr:
        if i > 127:
            rus_word += chr(i + 848)
        else:
            rus_word += chr(i)
    return rus_word
def get_pass(d):
    p = ''
    for i in d:
        p += hex(i).replace('0x', '')[::-1]
    return p[::-1]
print(crcok(b'\x02\x04\x02\x08\x01\x01\xc9'))