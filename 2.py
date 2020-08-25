import serial
import threading
import time
import datetime
from termcolor import colored, cprint

port = 'COM8'
baud = 19200

serial_port = serial.Serial(port, baud, timeout=100)
serial_port.parity = 'N'
serial_port.stopbits = 2
serial_port.flushInput()
serial_port.flushOutput()

rs485 = 'A'
buf_tail = -52


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
    cd = data[-1]
    if cd == c1:
        return True
    else:
        return False


def make_packet(adr, pdu):
    a = adr + pdu
    crc = crc8540(a)
    a += bytes([crc])
    print(len(a))
    return a


def get_rus(arr):
    rus_word = ''
    for i in arr:
        if i > 127:
            rus_word += chr(i + 848)
        else:
            rus_word += chr(i)
    return rus_word


def handle_rsA(dd):
    if dd[0] == 0x02:  # miru
        hanlde_miru(dd)
    elif dd[0] == 0x03:  # power
        pass
    elif dd[0] == 0x05:  # mmt
        pass
        # hanlde_mmt(dd)


def handle_rsB(dd):
    dt = datetime.datetime.now().strftime("%H:%M:%S")
    if dd[0] == 0x19:
        fl = dd[0] - 10
        if dd[1] == 0x01 and dd[2] == 0x08:
            print(dt, colored(f"ИЭМ{fl} ответ 12 байт ->", 'yellow'), dd[:12], crcok(dd[:12]))

        elif dd[1] == 0x04 and dd[2] == 0x02:
            print(dt, colored(f"запрос ИЭМ{fl} 6 байт ->", 'magenta'), dd[:6], crcok(dd[:6]))

        elif dd[1] == 0x10 and dd[2] == 0x02:
            print(dt, colored(f"ответ команды ИЭМ{fl} 6 байт ->", 'green'), dd[:6], crcok(dd[:6]))
        elif dd[1] == 0x18 and dd[2] == 0x01:
            print(dt, colored(f"команада на измнение ИЭМ{fl} 5 байт ->", 'green'), dd[:5], crcok(dd[:5]))
        elif dd[1] == 14 and dd[2] == 48:
            print(dt, colored(f"команада на измнение настроек ИЭМ{fl} 52 байта!!! ->", 'blue'), dd[:52], crcok(dd[:52]))
        elif dd[1] == 0x0c and dd[2] == 0x01:
            print(dt, colored(f"ПУСК/ПОЖАР!!! ИЭМ{fl} 5 байта!!! ->", 'red'), dd[:5], crcok(dd[:5]))
        else:
            pass
            print(dt, f"неизветсная команда ИЭМ{fl} 6 байт ->", dd.title())


def hanlde_mmt(dd):
    dt = datetime.datetime.now().strftime("%H:%M:%S")
    fl = dd[0] - 10
    if dd[1] == 0x01 and dd[2] == 0x08:
        print(dt, f"ИЭМ{fl} ответ 12 байт ->", dd[:13], crcok(dd[:13]))
    elif dd[1] == 0x04 and dd[2] == 0x13:
        print(dt, f"запрос ИЭМ{fl} 6 байт ->", dd[:23], crcok(dd[:23]))
    elif dd[1] == 0x10 and dd[2] == 0x02:
        print(dt, f"ответ команды ИЭМ{fl} 6 байт ->", dd[:6], crcok(dd[:6]))
    else:
        pass
        print(dt, f"неизветсная команда ИЭМ{fl} 6 байт ->", dd.title(), crcok(dd))


def get_pass(d):
    p = ''
    for i in d:
        p += hex(i).replace('0x', '')[::-1]
    return p[::-1]


s = set()


def hanlde_miru(dd):
    dt = datetime.datetime.now().strftime("%H:%M:%S")
    fl = dd[0] - 10
    if dd[1] == 0x01 and dd[2] == 0x08:
        pass
        #print(dt, colored(f"МИРУ ответ 12 байт ->", 'magenta'), dd[:12], crcok(dd[:12]))

    elif dd[1] == 0x04 and dd[2] == 0x02:
        pass
        #serial_port.write(b'\x02\x01\x08\x00\x00\x00\x00\x00\x00\x00\x00 ')
        print(dt, colored(f"МИРУ запрос ИЭМ{fl} 6 байт ->", 'yellow'), dd[:6], crcok(dd[:6]))
    elif dd[1] == 0x05 and dd[2] == 0x08:
        print(dt, colored(f"МИРУ время 12 байт ->", 'green'), dd[:12], crcok(dd[:12]))


    elif dd[1] == 37:
        if dd[2] == 0x04:
            print(dt, colored(f"МИРУ запрос неиспрвности 8 байт -> {dd[:8]}", 'red'))
        else:
            lendt = dd[2] + 4
            print(dt, colored(f"МИРУ ответ о неисправноти: адрес{dd[3]} 8 байт ->", 'blue'), get_rus(dd[5:lendt - 1]), crcok(dd[:lendt]), dd)

    elif dd[1] == 38:
        if dd[2] == 0x04:
            print(dt, colored(f"МИРУ запрос неиспрвности 8 байт -> {dd[:8]}", 'red'))
        else:
            lendt = dd[2] + 4
            print(dt, colored(f"МИРУ ответ о неисправноти: адрес{dd[3]} 8 байт ->", 'blue'), get_rus(dd[5:lendt - 1]), crcok(dd[:lendt]), dd)

    elif dd[1] == 0x17:
        if dd[2] == 0x04:
            print(dt, colored(f"МИРУ запрос сост упрв 8 байт -> {dd[:8]}", 'red'), crcok(dd[:8]))
        else:
            lendt = dd[2] + 4
            print(dt, colored(f"МИРУ ответ о сост упрв: адрес 8 байт ->", 'blue'), get_rus(dd[3:lendt - 1]),
                  crcok(dd[:lendt]), dd)


    elif dd[1] == 36 :
        if dd[2] == 0x00:
            print(dt, colored(f"МИРУ запрос о списке неис... 4байт ->", 'yellow'), (dd[:4]), crcok(dd[:4]))
        elif dd[2] == 0x04:
            print(dt, colored(f"МИРУ ответ о списке неис... 8байт ->", 'yellow'), (dd[:8]), crcok(dd[:8]))

    elif dd[1] == 0x1b:
        if dd[2] == 0x04:
            print(dt, colored(f"МИРУ ответ о списке  8байт ->", 'yellow'), (dd[:8]), crcok(dd[:8]))

    elif dd[1] == 0x18 :
        if dd[2] == 0x04:
            print(dt, colored(f"МИРУ запрос о управлении  8байт ->", 'white'), (dd[:8]), crcok(dd[:8]))
        elif dd[2] == 0x00:
            print(dt, colored(f"МИРУ ответ о управлении  8байт ->", 'white'), (dd[:4]), crcok(dd[:4]))

    elif dd[1] == 0x0b:
        if dd[2] == 0x04:
            print(dt, colored(f"ввод пароля ->{get_pass(dd[3:6])}", 'green'), dd[:12], crcok(dd[:12]))
        elif dd[2] == 0x00:
            print(dt, colored(f"ввод  пароль ок", 'green'), dd[:4], crcok(dd[:4]))

    elif dd[1] == 0x1d or dd[1] == 0x1c:
        if dd[2] == 0x04:
            print(dt, colored(f"МИРУ запрос прибора 8 байт -> {dd[:8]}", 'red'))
        else:
            lendt = dd[2] + 4
            print(dt, colored(f"МИРУ ответ о приборе 8 байт ->", 'blue'), get_rus(dd[5:lendt - 1]),
                crcok(dd[:lendt]))

    elif dd[1] == 0x10:
            lendt = 32
            print(dt, colored(f"МИРУ событие для гл меню 8 байт ->", 'blue'), get_rus(dd[10:lendt - 1]),
                crcok(dd[:32]), dd[:32])
    else:
        pass
        if dd[1] == 0x04 or dd[1] == 0x02 or dd[1] == 65 or dd[1] == 0x01 or dd[1] == 68:
            return
        print(dt, f"неизветсная команда ИЭМ{fl} 6 байт ->", dd, crcok(dd))


def read_from_port(ser):
    connected = False
    rx_buff = bytearray()
    while not connected:
        connected = True
        while True:
            dd = ser.read_all()  # читаем байт
            if len(dd) != 0:
                if rs485 == 'A':
                    try:
                        handle_rsA(dd)
                    except:
                        print('eerrr')
                elif rs485 == 'B':
                    handle_rsB(dd)


def write_port(ser):
    connected = False
    while not connected:
        # serin = ser.read()
        connected = True
        # неиспрвность 24в си со тбл
        while True:
            input("send packet IEM25 ->")

            ser.write(b'\x02\x10\x1cY\x07\x14\x01\x15\x06 \x00\xcc\xce\xd3       \xd1\xc1\xd0\xce\xd1  \x00\x00\x00\xd5')
            # time.sleep(0.1)
            # ser.write(b'\x0b\x18\x01\x04^')
            # ser.write(b'\x19\x04\x02\x02\x04>')
            # 05\n\x00\xd2\x02\x04 - mmt
            # \x02\x04\x02\x02\x042' -miru
            # \x03\x04\x02\x02\x04\xff' -power
            time.sleep(0.5)
        # ser.write(b'\x19\x04\x02\x02\x04>')


thread = threading.Thread(target=read_from_port, args=(serial_port,))
tx = threading.Thread(target=write_port, args=(serial_port,))
thread.start()
tx.start()
