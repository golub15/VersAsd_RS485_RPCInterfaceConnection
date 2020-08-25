import serial
import threading
import multiprocessing
import time
import paho.mqtt.client as mqtt
import json
from collections import deque

OBJECT_ID = "01_14_1"

FLOORS_COUNT = 14  # кол-во этажей
COM_PORT = "COM8"
MQTT_SERVER_IP = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_USERNAME = ''
MQTT_PASSWORD = ''
MQTT_KEEPALIVE_TIME = 15


SERIAL_BAUDRATE = 19200
SERIAL_RECONNECTION_TIME = 5

PING_REQ_PACKET_PREFIX = b''
PING_RESP_PACKET_PREFIX = b''
TIME_CHANGED_PACKET_PREFIX = b''
DISPLAY_EVENT_PACKET_PREFIX = b''

MIRU_ADDRESS = b'\x02'

PACKET_RESEND_COUNT = 6
MOU_CONNECTION_TIMEOUT = 2  # SECONDS

response_comands = {
    b'\x04\x02': [6, 'ping'],
    b'\x05\x08': [12, 'time'],
    b'\x10\x1c': [32, 'display_event'],
    b'\xff\x00': [2, 'com_port_0'],
    b'\xff\x01': [2, 'com_port_1'],
    b'\xff\x02': [2, 'mou_0'],
    b'\xff\x03': [2, 'mou_1'],
    b'\xff\xff': [2, 'packet_timeout'],
    b'\x1b\x04': [4, 'device_number'],
    b'\x18\x00': [4, 'control_device'],
    b'\x0b\x00': [4, 'password'],
    b'\n\x00': [4, 'sys_reset'],
    b'\x24': [8, 'error_number'],
    b'\x25': [lambda x: x[1] + 4, 'error_data'],
    b'\x26': [lambda x: x[1] + 4, 'error_data'],
    b'\x17': [lambda x: x[1] + 4, 'control_state'],
    b'\x1d': [lambda x: x[1] + 4, 'device_info'],
    b'\x1c': [lambda x: x[1] + 4, 'device_info'],

}
template = {

    "MIRU": {
        "mode": "2",
        "power": "0",
        "fire_1": "0",
        "fire_2": "0",
        "alarm": "0",
        "error": "0",
    },

    "mou": {
        "device": "ОК",
        "siren": "ОК",
        "exit_panel": "ОК",
        "fire_light": "ОК",
        "pomp_1": "ОК",
        "pomp_2": "ОК",
        "pomp_3": "ОК",
        "shleif_1": "ОК",
        "shleif_2": "ОК",
        "shleif_3": "ОК",
        "shleif_4": "ОК",
    },

    "IEM": {
        "device": "ОК",
        "air_gate_in": "ОК",
        "air_gate_out": "ОК",
        "siren": "ОК",
        "exit_panel": "ОК",
        "fire_light": "ОК",
        "shleif_1": "ОК",
        "shleif_2": "ОК",
        "shleif_3": "ОК",
        "shleif_4": "ОК",
        "shleif_5": "ОК",
        "shleif_6": "ОК",
        "shleif_7": "ОК",
        "shleif_8": "ОК",
    },

    "MTE": {
        "device": "ОК",
        "air_gate_in": "ОК",
        "air_gate_out": "ОК",
        "fan_in": "ОК",
        "fan_out": "ОК",
        "heat": "ОК",
        "shleif_1": "ОК",
        "shleif_2": "ОК",
        "shleif_3": "ОК",
        "shleif_4": "ОК",
    }
}


def crc8540(pcBlock):
    lb = len(pcBlock) - 1
    b = 0
    for b2 in pcBlock:
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


def make_packet(pdu):
    a = bytes(b'\x02') + pdu
    crc = crc8540(a)
    a += bytes([crc])
    return a


def get_rus(arr):
    rus_word = ''
    for i in arr:
        if i > 127:
            rus_word += chr(i + 848)
        elif i == 0:
            rus_word += ''
        else:
            rus_word += chr(i)
    return rus_word


def get_pass(d):
    p = ''
    for i in d:
        p += hex(i).replace('0x', '')[::-1]
    return p[::-1]


class MOU_Communication:

    def run(self):
        pass

    def __init__(self, com_port):
        #  serial thread
        self.serial_port = serial.Serial()
        self.serial_port.port = com_port
        self.serial_port.baudrate = 19200
        self.serial_port.stopbits = 1
        # self.serial_port.set_buffer_size(64, 64)
        self.com_connect = 1

        self.serial_requests = multiprocessing.Queue()
        self.serial_responses = multiprocessing.Queue()
        self.serial_events = multiprocessing.Queue()

        self.mou_connect = 0
        self.com_state = 0
        self.mou_mode = -1
        self.mou_power = -1
        self.mou_fire1 = -1
        self.mou_fire2 = -1
        self.mou_err = -1
        self.mou_alarm = -1

        self.command_requests = deque()
        self.command_responses = deque()
        self.command_events = deque()

        self.com_port = threading.Thread(target=self.handle_com_port,
                                         args=(self.serial_requests, self.serial_responses, self.serial_events))
        self.com_port.start()

        # self.com_port.join()

        def update_system(serial_events: multiprocessing.Queue):
            while 1:
                time.sleep(0.001)
                # print("pass")
                if self.serial_events.qsize() > 0:
                    topic, payload = self.serial_events.get()
                    # print(topic, payload)
                    if topic == 'display_event':
                        # print(payload)
                        payload = get_rus(payload[9:30])
                    elif topic == 'mou_state':
                        self.mou_connect = payload
                    elif topic == 'mou_mode':
                        self.mou_mode = payload

                    self.command_events.append((topic, payload))

        self.us = threading.Thread(target=update_system, args=(self.serial_events,))

        self.us.start()

        # self.us.join()

    def handle_com_port(self, serial_requests: multiprocessing.Queue, serial_responses: multiprocessing.Queue,
                        serial_events: multiprocessing.Queue):

        com_state = -1
        mou_state = -1
        last_time_mou = 0
        serial_requests_lock = 0
        response_lock = 0
        request_failed_counter = 0
        serial_request_last_packet = b''

        last_ping = 0

        serial_events.put(('com_port', 0))
        serial_events.put(('mou_state', 0))

        while 1:
            time.sleep(0.0001)

            if not self.serial_port.is_open:
                try:
                    self.serial_port.open()
                    if com_state != 1:
                        com_state = 1
                        serial_events.put(('com_port', 1))
                    while not serial_requests.empty():
                        serial_requests.get()
                    while not serial_responses.empty():
                        serial_responses.get()

                except serial.SerialException:
                    pass
                    time.sleep(5)
            else:
                try:

                    if mou_state and time.time() - last_time_mou > 2 and last_time_mou != 0:
                        mou_state = 0
                        serial_events.put(('mou_state', 0))

                    if self.serial_port.in_waiting > 0:
                        packet = self.serial_port.read(self.serial_port.in_waiting)
                    else:
                        continue

                    if len(packet) != 0 and packet[0] == 2 and crcok(packet):
                        print(packet)
                        last_time_mou = time.time()
                        if mou_state != 1:
                            mou_state = 1
                            serial_events.put(('mou_state', 1))

                        if packet[1:3] != b'\x02\x04' and packet[1:3] != b'\x04\x02':

                            if packet[1:3] != b'\x05\x08' and packet[1:3] != b'\x10\x1c':
                                if serial_requests_lock:
                                    if not response_lock:
                                        serial_responses.put(packet[1:])
                                        response_lock = 1
                                        request_failed_counter = 0
                            else:
                                if packet == b'\x02\x01\x08\x00\x00\x00\x00\x00\x00\x00\x00 ':
                                    print('disconect miru!!!')
                                    continue
                                if packet[1:3] != b'\x05\x08':
                                    serial_events.put(('display_event', packet[1:]))
                                elif packet[1:3] != b'\x10\x1c':
                                    serial_events.put(('time_event', packet[1:]))

                        else:
                            if last_ping != packet:
                                serial_events.put(('ping', packet))

                            last_ping = packet
                            if serial_requests_lock:
                                if response_lock:
                                    serial_requests_lock = 0
                                    response_lock = 0
                                else:
                                    request_failed_counter += 1
                                    if request_failed_counter > 2:
                                        request_failed_counter = 0
                                        serial_responses.put(b'\xff\xff')
                                        # print('timeout')
                                    serial_requests_lock = 0

                        if not serial_requests_lock:
                            if request_failed_counter == 0 and serial_requests.qsize() > 0:
                                p = serial_requests.get()
                                self.serial_port.write(p)  # o(1)
                                serial_request_last_time = time.time()
                                serial_request_last_packet = p
                                serial_requests_lock = 1
                                continue

                            elif request_failed_counter > 0:
                                self.serial_port.write(serial_request_last_packet)
                                serial_requests_lock = 1
                                continue

                            # serial_request_last_time = time.time()

                        self.serial_port.write(b'\x02\x01\x08\x00\x00\x00\x00\x00\x00\x00\x00 ')

                except serial.SerialException:
                    self.serial_port.close()
                    serial_events.put(('com_port', 0))
                    serial_events.put(('mou_state', 0))
                    mou_state = 0
                    com_state = 0
                    while not serial_requests.empty():
                        serial_requests.get()
                    while not serial_responses.empty():
                        serial_responses.get()
                    # print('clear')

    def get(self, data):
        if not self.mou_connect:
            g = []
            for i in range(len(data)):
                g.append(('mou_disconnected', 1))
            return g

        t = 0
        while not self.serial_requests.empty():
            self.serial_requests.get()
        while not self.serial_responses.empty():
            self.serial_responses.get()

        for x in data:
            self.serial_requests.put(x)

        t = time.time()
        g = len(data)
        r = []
        while 1:
            time.sleep(0.0001)
            if not self.mou_connect:
                g = []
                for i in range(len(data)):
                    g.append(('mou_disconnected', 1))
                return g

            if time.time() - t > 5:
                g = []
                for i in range(len(data)):
                    g.append(('packet_timeout', 1))
                return g

            if self.serial_responses.qsize() > 0:
                t = time.time()
                s = (self.serial_responses.get(), 0)
                r.append(s)
                if len(r) == g:
                    return r


class vers_asd:

    def __init__(self):

        self.asd = MOU_Communication(COM_PORT)
        #  command handler threa
        self.commands_queue = deque()
        self.display_events = deque()
        self.listen_display_events = 0

        #  env thread

        self.env_requests = deque()
        self.env_responses = deque()
        self.env_callback = None
        self.current_update = 0

        self.gg = 0

        self.us = threading.Thread(target=self.update_system, args=())
        self.us.start()

        self.tx_task = threading.Thread(target=self.send_data, args=())
        self.tx_task.start()

    def switch_mode(self, topic, args, call, call_id):
        if 'password' not in args and 'mode' not in args:
            call('args err', 1, call_id)
            return
        if len(args['password']) != 6:
            call('args err', 1, call_id)
            return

        if args['mode'] == 'A':
            password = '000000'
        else:
            password = args['password']

        bp1 = bytearray.fromhex(password[:2])
        bp2 = bytearray.fromhex(password[2:4])
        bp3 = bytearray.fromhex(password[4:6])

        p = make_packet(b'\x0b\x04' + bp3 + bp2 + bp1 + b'\x00')
        print(p)
        payload, err = self.asd.get([p])[0]
        if err:
            call('switch_mode err: ' + payload, 1, call_id)
            return
        if payload == b'\x0b\x00l':
            call('ok', 0, call_id)
            return
        elif payload == b'\x03\x00\x1a':
            call('wrong password', 1, call_id)
            return
        else:
            # print(payload)
            call('payload error', 1, call_id)
            return

    def reset_system(self, topic, args, call, call_id):
        if 'password' not in args:
            call('args error', 1, call_id)
            return
        bp = bytearray.fromhex(args['password'])
        payload, err = self.asd.get([make_packet(b'\n\x04' + bp + b'\x00\x00\x00')])[0]
        if err:
            call('reset_sys err: ' + payload, 1, call_id)
            return
        if payload == b'\n\x00\xa8':
            call('ok', 0, call_id)
            return
        elif payload == b'\x03\x00\x1a':
            call('wrong password', 1, call_id)
            return
        else:
            call('payload error', 1, call_id)
            return

    def run_fire(self, topic, args, call, call_id):
        if 'floor' not in args:
            call('args error', 1, call_id)
            return
        floor = int(args['floor'])
        if floor == 0:
            pass
        else:
            floor += 10
        payload, err = self.asd.get([make_packet(b'\x0c\x04' + bytearray([floor]) + b'\x00\x00\x00')])[0]
        if err:
            call('run_fire err: ' + payload, 1, call_id)
            return
        if payload == b'\x0c\x00\x02':
            call('ok', 0, call_id)
            return
        elif payload == b'\x03\x00\x1a':
            call('floor unavailable', 1, call_id)
            return
        else:
            call('payload error', 1, call_id)
            return

    def set_time(self, topic, args, call, call_id):
        pass

    def control_relay(self, topic, args, call, call_id):
        print(args, call_id)
        if not ('state' in args and 'element' in args and 'address' in args):
            call('args error', 1, call_id)
            return
        arp = self.asd.get([make_packet(b'\x16\x04' + bytearray([args['address']]) + b'\x00\x00\x00'),
                            make_packet(b'\x17\x04' + bytearray([args['element']]) + b'\x00\x00\x00')])

        payload, err = arp[0]
        # print(payload)
        if err:
            call('relay device info error: ' + payload, 1, call_id)
            return
        # print(payload, err)

        if args['state'] == -1:
            payload, err = self.asd.get([make_packet(b'\x18\x04' + bytearray([args['element']]) + b'\x00\x00\x00')])[0]
            if err:
                call('relay control error: ' + payload, 1, call_id)
                return
            else:
                call('ok ', 0, call_id)
                return

        payload, err = arp[1]

        if err:
            call('relay element info error: ' + payload, 1, call_id)
            return

        ld = payload[1] + 3
        element_state = get_rus(payload[2:ld - 1])

        state = args['state']

        if 'вкл' in element_state or 'откр' in element_state:
            if state:
                payload, err = \
                    self.asd.get([make_packet(b'\x18\x04' + bytearray([args['element']]) + b'\x00\x00\x00')])[0]
                if err:
                    call('relay control error: ' + payload, 1, call_id)
                    return

                r = 1
                if r:
                    time.sleep(5)
                    call('ok', 0)
                else:
                    call('relay control error: not accepted', 1, call_id)
                # print(payload)
            else:
                call('relay already off', 1, call_id)
                # print(payload, state, element_state)
        elif 'выкл' in element_state or 'закр' in element_state:
            if not state:
                payload, err = \
                    self.asd.get([make_packet(b'\x18\x04' + bytearray([args['element']]) + b'\x00\x00\x00')])[0]
                if err:
                    call('relay control error: ' + payload, 1, call_id)
                    return

                r = 1
                if r:
                    time.sleep(5)
                    call('ok', 0)
                else:
                    call('relay control error: not accepted', 1, call_id)
            else:
                call('relay already on', 1)
                # print(payload, state, element_state)
        else:
            call('control_relay  el state err' + str(payload), 1, call_id)

    def update_system(self):
        commands_lock = 0
        call = None

        def shell_command(func, t, a, c, call_id):
            try:
                func(t, a, c, call_id)
            except:
                c(str(func) + ' func expect', 1, call_id)

        while 1:
            time.sleep(0.0001)
            if len(self.commands_queue) > 0:
                data = self.commands_queue.popleft()
                topic, args, call, call_id = data[0], data[1], data[2], data[3]

                if topic == 'get_err':
                    pass
                    # shell_command(self.get_err, topic, args, call)
                elif topic == 'control_relay':
                    shell_command(self.control_relay, topic, args, call, call_id)
                elif topic == 'reset_system':
                    shell_command(self.reset_system, topic, args, call, call_id)
                elif topic == 'switch_mode':
                    shell_command(self.switch_mode, topic, args, call, call_id)
                elif topic == 'run_fire':
                    shell_command(self.run_fire, topic, args, call, call_id)

    def send_command(self, topic, args, callback, call_id='none'):
        self.commands_queue.append((topic, args, callback, call_id))

    def send_data(self):
        def clg(p, e):
            self.gg += 1
            print(p, e)

        f = 0
        while 1:
            time.sleep(0.01)

            s = input('команада: ')

            if s == "0":

                # print('now tablo will', f)
                self.send_command('control_relay', {'mode': 'toggle', 'address': 11, 'element': 0, 'state': f}, clg)
                # self.send_command('control_relay', {'address': 1, 'element': 1, 'state': f}, clg)
                # self.send_command('control_relay', {'address': 1, 'element': 2, 'state': f}, clg)
                # self.send_command('control_relay', {'address': 1, 'element': 0, 'state': 0}, clg)
                f = not f


            elif s == '3':
                # 12:20:03 ввод пароля ->123459 b'\x02\x0b\x04Y4\x12\x00\xeb' True
                self.send_command('run_fire', {'floor': 15}, clg)
            elif s == '5':
                self.send_command('reset_system', {'password': '00'}, clg)
            elif s == '9':
                self.send_command('switch_mode', {'password': '123456', 'mode': 'A'}, clg)
                # print(a)


class Server_Communication:

    def mqtt_subscribe(self):
        self.client.subscribe(f'{self.object_id}/rpc/req', qos=2)

    def mqtt_on_message(self, client, userdata, msg):

        def resp(p, e, call_id):
            d = json.dumps({'payload': p, 'error': e, "call_id": call_id})
            self.client.publish(f'{self.object_id}/rpc/resp', d)

        # print("Message received. Topic: {}. Payload: {}".format(
        # msg.topic,
        # s#tr(msg.payload)))
        a = str(msg.payload)[2:-1]
        args = eval(a)
        if self.mou_state != 'con':
            self.client.publish('01_14_1/rpc/resp',
                                str({'payload': 'mou_not_con', 'error': 1, "call_id": args['call_id']}))

        self.device.send_command(args['command'], args['data'], resp, args['call_id'])
        # print(args)

    def mqtt_on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Result from connect: {}".format(
            mqtt.connack_string(rc)))
        self.mqtt_subscribe()
        client.publish(f'{self.object_id}/con/client', '1', 0, 1)  # client avb
        self.client.publish(f"{self.object_id}/con/port", self.con_port, 0, 1)
        self.client.publish(f"{self.object_id}/con/mou", self.con_mou, 0, 1)

        self.client.publish(f"{self.object_id}/states/mou", str(self.mou_state), 0, 1)
        if self.mou_state == 'con':
            self.send_state(0)

    def mqtt_on_subscribe(self, client, userdata, mid, granted_qos):
        print("I've subscribed with QoS: {}".format(
            granted_qos[0]))

    def __init__(self):
        global template

        self.object_id = OBJECT_ID
        self.mqtt_server = MQTT_SERVER_IP
        self.client = mqtt.Client(client_id=self.object_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set('', '')

        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.on_subscribe = self.mqtt_on_subscribe

        self.mou_state = 'not_con'
        self.mou_init = 0
        self.mou_init_time = 0

        self.device = vers_asd()

        self.reset = 0
        self.reset_time = 0
        self.events_listen = 1
        self.elements_states = {}

        self.con_port = 0
        self.con_mou = 0

        for i in range(1, 16):
            self.elements_states[f"iem_{i}"] = dict(template['IEM'])
        self.elements_states['iem_0'] = dict(template['mou'])
        self.elements_states['iem_50'] = dict(template['MTE'])
        self.miru_states = dict(template['MIRU'])

        self.client.will_set(f'{self.object_id}/con/client', '0', 0, 1)

        try:
            self.client.connect(host=self.mqtt_server, port=1883, keepalive=10)
        except ConnectionRefusedError:
            pass

        self.mqtt_loop_task = threading.Thread(target=self.mqtt_loop, args=())
        self.mqtt_loop_task.start()

        time.sleep(4)

        self.handle_system_t = threading.Thread(target=self.handle_system, args=())
        self.handle_system_t.start()

    def mou_state_set(self, st):
        print('mou mqtt: ', st)
        self.mou_state = st
        self.client.publish(f"{self.object_id}/states/mou", str(self.mou_state), 0, 1)

    def send_state(self, arg):
        if arg == 1 or arg == 0:
            f = json.dumps(self.elements_states)
            self.client.publish(f"{self.object_id}/states/floors", str(f), 0, 1)
        if arg == 2 or arg == 0:
            mid = json.dumps(self.miru_states)
            self.client.publish(f"{self.object_id}/states/miru", str(mid), 0, 1)

    def mqtt_loop(self):
        self.client.loop_forever()

    def reset_callback(self, p, e, call_id):
        if not e:
            self.reset_time = time.time()
            self.reset = 1
            events_listen = 1
            for k, v in self.elements_states.items():
                for e, s in v.items():
                    self.elements_states[k][e] = "ОК"
            self.send_state(1)

            # print(str(self.elements_states))
        else:
            self.mou_state_set('error state reset')
            print('error 1')

    def handle_system(self):

        while 1:
            time.sleep(0.0001)

            if self.reset and time.time() - self.reset_time > 35:
                self.reset = 0
                self.mou_state_set('con')
                # self.events_listen = 1
                self.send_state(1)

            if self.mou_init and time.time() - self.mou_init_time > 20:
                self.mou_init = 0
                self.mou_state_set('reset')
                self.device.send_command('reset_system', {'password': '00'}, self.reset_callback, "f00000")

            if len(self.device.asd.command_events) > 0:
                topic, payload = self.device.asd.command_events.popleft()

                if topic == "mou_state":
                    self.con_mou = str(payload)
                    self.client.publish(f"{self.object_id}/con/mou", self.con_mou, 0, 1)

                    if payload:
                        self.mou_state_set('init')
                        self.mou_init = 1
                        self.mou_init_time = time.time()

                    else:
                        self.mou_state_set('not_con')
                        self.mou_init = 0
                        self.events_listen = 0
                        self.reset = 0

                elif topic == 'display_event':
                    if not self.reset and 'СБРОС' in payload:
                        self.mou_init = 0
                        self.mou_state_set('reset')
                        self.reset = 1
                        self.reset_time = time.time()
                        for k, v in self.elements_states.items():
                            for e, s in v.items():
                                self.elements_states[k][e] = "ОК"
                    if self.mou_init:
                        continue
                    if payload[:3] in ["ИЭМ", "МТЭ", "МОУ"] and len(payload) > 12:
                        device_type = payload[:3]
                        num = 0
                        if device_type == "ИЭМ":
                            num = f"iem_{str(int(payload[3:5]))}"
                        elif device_type == "МТЭ":
                            num = 'iem_50'
                        elif device_type == "МОУ":
                            num = 'iem_0'

                        # print(num, payload)

                        def get_shleif(payload):
                            try:
                                for i in len(payload):
                                    if payload[i] == 'Ш':
                                        sh = int(payload[i + 1])
                                        return sh
                            except:
                                print("sh err", payload)
                                return 1

                        if num in self.elements_states:
                            if "НЕТ ОТВ" in payload:
                                self.elements_states[num]["device"] = "НЕТ ОТВЕТА"
                                for k, v in self.elements_states[num].items():
                                    if k != "device":
                                        self.elements_states[num][k] = "НЕТ СВЯЗИ"
                            elif "ОТВЕТ" in payload:
                                self.elements_states[num]["device"] = "ОК"
                                for k, v in self.elements_states[num].items():
                                    if k != "device":
                                        self.elements_states[num][k] = "ОК"
                            elif "НЕИСПР" in payload:
                                if "К1" in payload:
                                    self.elements_states[num]["air_gate_in"] = "НЕИСПР"
                                elif "К2" in payload:
                                    self.elements_states[num]["air_gate_out"] = "НЕИСПР"
                                elif "СИР" in payload:
                                    self.elements_states[num]["siren"] = "НЕИСПР"
                                elif "СО" in payload:
                                    self.elements_states[num]["fire_light"] = "НЕИСПР"
                                elif "ТБЛ" in payload:
                                    self.elements_states[num]["exit_panel"] = "НЕИСПР"
                                elif "Ш" in payload:
                                    self.elements_states[num][f"shleif_{get_shleif(payload)}"] = "НЕИСПР"
                                elif "ВВ" in payload:
                                    self.elements_states[num]["fan_in"] = "НЕИСПР"
                                elif "ВП" in payload:
                                    self.elements_states[num]["fan_in"] = "НЕИСПР"
                                elif "НГР" in payload:
                                    self.elements_states[num]["heat"] = "НЕИСПР"
                                elif "НП1" in payload:
                                    self.elements_states[num]["pomp_1"] = "НЕИСПР"
                                elif "НП2" in payload:
                                    self.elements_states[num]["pomp_2"] = "НЕИСПР"
                                elif "НДР" in payload:
                                    self.elements_states[num]["pomp_3"] = "НЕИСПР"
                                elif "24В" in payload:
                                    self.elements_states[num]["device"] = "НЕИСПР"
                                elif "ЛИН" in payload:
                                    h = range(1, 9)
                                    if device_type == "mte" or device_type == "mou":
                                        h = range(1, 5)
                                    for x in h:
                                        self.elements_states[num][f"shleif_{str(x)}"] = "27В НЕИСПР"
                            elif "НОРМА" in payload:
                                if "Ш" in payload:
                                    self.elements_states[num][f"shleif_{get_shleif(payload)}"] = "10"
                            elif "ПОЖАР1" in payload:
                                if "Ш" in payload:
                                    self.elements_states[num][f"shleif_{get_shleif(payload)}"] = "ПОЖ 1"
                            elif "ПОЖАР2" in payload:
                                if "Ш" in payload:
                                    self.elements_states[num][f"shleif_{get_shleif(payload)}"] = "ПОЖ 2"
                                else:
                                    self.elements_states[num]["device"] = "ПОЖ 2"

                                if self.device.asd.mou_mode == 1:
                                    self.elements_states[num]["air_gate_in"] = "ВКЛ"
                                    self.elements_states[num]["air_gate_out"] = "ВКЛ"
                                    self.elements_states[num]["exit_panel"] = "ВКЛ"
                                    self.elements_states[num]["fire_light"] = "ВКЛ"
                                    self.elements_states[num]["siren"] = "ВКЛ"

                                    self.elements_states["mte"]["air_gate_in"] = "ВКЛ"
                                    self.elements_states["mte"]["air_gate_out"] = "ВКЛ"
                                    self.elements_states["mte"]["fan_in"] = "ВКЛ"
                                    self.elements_states["mte"]["fan_out"] = "ВКЛ"

                            elif "ВКЛ" in payload:
                                if "СИР" in payload:
                                    self.elements_states[num]["siren"] = "ВКЛ"
                                elif "СО" in payload:
                                    self.elements_states[num]["fire_light"] = "ВКЛ"
                                elif "ТБЛ" in payload:
                                    self.elements_states[num]["exit_panel"] = "ВКЛ"
                                elif "ВП" in payload:
                                    self.elements_states[num]["fan_in"] = "ВКЛ"
                                elif "ВВ" in payload:
                                    self.elements_states[num]["fan_out"] = "ВКЛ"
                                elif "НГР" in payload:
                                    self.elements_states[num]["heat"] = "ВКЛ"
                                elif "НП1" in payload:
                                    self.elements_states[num]["pomp_1"] = "ВКЛ"
                                elif "НП2" in payload:
                                    self.elements_states[num]["pomp_2"] = "ВКЛ"
                                elif "НДР" in payload:
                                    self.elements_states[num]["pomp_3"] = "ВКЛ"
                            elif "ВЫКЛ" in payload:
                                if "СИР" in payload:
                                    self.elements_states[num]["siren"] = "ОК"
                                elif "СО" in payload:
                                    self.elements_states[num]["fire_light"] = "ОК"
                                elif "ТБЛ" in payload:
                                    self.elements_states[num]["exit_panel"] = "ОК"
                                elif "ВП" in payload:
                                    self.elements_states[num]["fan_in"] = "ОК"
                                elif "ВВ" in payload:
                                    self.elements_states[num]["fan_out"] = "ОК"
                                elif "НГР" in payload:
                                    self.elements_states[num]["heat"] = "ОК"
                                elif "НП1" in payload:
                                    self.elements_states[num]["pomp_1"] = "ОК"
                                elif "НП2" in payload:
                                    self.elements_states[num]["pomp_2"] = "ОК"
                                elif "НДР" in payload:
                                    self.elements_states[num]["pomp_3"] = "ОК"
                                    # if r != "":
                            elif "ОТКРЫТ" in payload:
                                if "К1" in payload:
                                    self.elements_states[num]["air_gate_in"] = "ВКЛ"
                                elif "К2" in payload:
                                    self.elements_states[num]["air_gate_out"] = "ВКЛ"
                            elif "ЗАКРЫТ" in payload:
                                if "К1" in payload:
                                    self.elements_states[num]["air_gate_in"] = "ОК"
                                elif "К2" in payload:
                                    self.elements_states[num]["air_gate_out"] = "ОК"

                                    # if r != "":
                    elif payload[:3] in ["МИП"]:
                        if "220" in payload:
                            # print("220 volt")
                            self.miru_states['power'] = '1'
                        elif "АКБ" in payload:
                            # print("akuma err")
                            self.miru_states['power'] = '2'

                        self.send_state(2)
                    self.send_state(1)
                    self.client.publish(f"{self.object_id}/events/display", payload, 0, 1)
                elif topic == 'ping':

                    try:
                        d0 = bin(payload[3])[2:]
                        d1 = bin(payload[4])[2:]

                        d0 = '0' * (8 - len(d0)) + d0
                        d1 = '0' * (8 - len(d1)) + d1

                        if d0[7] == '1':
                            self.miru_states['mode'] = '1'
                        if d0[6] == '1':
                            self.miru_states['mode'] = '2'
                        self.miru_states['error'] = d1[5]
                        self.miru_states['fire_1'] = d1[3]
                        self.miru_states['fire_2'] = d1[7]
                        if self.miru_states['power'] != '0' and d1[4] == '0':
                            self.miru_states['power'] = '0'
                        self.miru_states['alarm'] = d1[6]
                    except:
                        pass

                    self.send_state(2)
                elif topic == 'com_port':
                    self.con_port = str(payload)
                    self.client.publish(f"{self.object_id}/con/port", self.con_port, 0, 1)

                self.client.publish(topic, payload, 0, 1)
                print(f"-{topic}-", payload)


if __name__ == '__main__':
    dd = Server_Communication()
