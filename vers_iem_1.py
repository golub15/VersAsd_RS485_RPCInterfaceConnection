
import paho.mqtt.client as mqtt
import  json
def on_connect(client, userdata, flags, rc):
    print("sdsResult from connect: {}".format(
        mqtt.connack_string(rc)))
    # Выполняем подписку на фильтр темы vehicles/vehiclepi01/tests
    client.subscribe('01_14_1/avb/port', qos=2)

    #h = {"iem_1": {'device': 'ПОЖ 2', 'air_gate_in': 'ВКЛ', 'air_gate_in': 'ВКЛ', 'siren': 'ВКЛ', 'exit_panel': 'ВКЛ', 'fire_light': 'ВКЛ', 'shleif_1': '0', 'shleif_2': '0', 'shleif_3': '0', 'shleif_4': '0', 'shleif_5': '0', 'shleif_6': '0', 'shleif_7': 'ПОЖ 2 ', 'shleif_8': '0'}}
   # f = json.dumps(h)
   # print(str(f))

    #client.publish('01_14_1/floors', f, 0, 1)

def on_subscribe(client, userdata, mid, granted_qos):
    print("I've subscribed with QoS: {}".format(
    granted_qos[0]))

def on_message(client, userdata, msg):
    print("Message received. Topic: {}. Payload: {}".format(
        msg.topic,
        str(msg.payload)))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

if __name__ == "__main__":
    client = mqtt.Client(client_id='a12', protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.username_pw_set('', '')
    try:
        client.connect(host='broker.emqx.io', port=1883, keepalive=5)
    except ConnectionRefusedError:
        pass
    client.loop_forever()