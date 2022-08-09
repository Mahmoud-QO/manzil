import serial
import json
import paho.mqtt.client as mqtt
from time import sleep

#### DEFINE ###################################################################

CLIENT_ID = 'SMART-HOME-ARDUINO-CLIENT'
BROKER_ADDRESS = 'localhost'
ROOT_TOPIC = 'mqtt/smart-home/v0'

#### GLOBAL ###################################################################

client = mqtt.Client(CLIENT_ID)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

#### CALLBACKS ################################################################

def on_connect(client, userdata, flags, rc):
    client.subscribe(ROOT_TOPIC + '/#')
    
def on_message(client, userdata, message):
    path = message.topic.replace(ROOT_TOPIC + '/', '')
    try:
        value = json.loads(str(message.payload.decode("utf-8")))
    except:
        value = str(message.payload.decode("utf-8"))
        
    doc = {}
    doc['path'] = path
    doc['value'] = value
    doc = json.dumps(doc) + '\n'

    ser.write(doc.encode('ascii'))

    print(">>>>  " + doc)

    # print(f">>>>  path: {path}, value: {value}, type: {type(value)}\n")
    #print("message topic = ",message.topic)
    #print("message qos = ",message.qos)
    #print("message retain flag = ",message.retain)

#### MAIN() ###################################################################

def main():
    ### Initialization ##############################

    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS)

    ser.reset_input_buffer()

    ### Loop ########################################

    client.loop_start()

    try:
        while True:
            sleep(0.2)

            if (ser.in_waiting > 0):
                line = ser.readline().decode('utf-8').rstrip()
                print(line)
                if (line[0] == '{' and line[-1] == '}'):
                    msg = json.loads(line)           
                    value = json.dumps(msg['value'])
                            
                    client.publish(ROOT_TOPIC + '/' + msg['path'], value, retain=False)

                    print(f"####  key: {msg['path']}, value: {value}, type: {type(value)}\n")
                else:
                    print(line + '\n')
        
    except KeyboardInterrupt:
        pass

    client.loop_stop()
    client.disconnect()

#### FUNCTIONS ################################################################

# millis = lambda: int(round(time() * 1000))

#### EXECUTE ##################################################################

if (__name__ == '__main__'): main()
