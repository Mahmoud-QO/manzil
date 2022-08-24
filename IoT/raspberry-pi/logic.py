import json
import paho.mqtt.client as mqtt
from time import sleep

#### DEFINE ###################################################################

CLIENT_ID = 'SMART-HOME-LOGIC-CLIENT'
BROKER_ADDRESS = '192.168.1.100'
ROOT_TOPIC = 'mqtt/smart-home/v0'

#### GLOBAL ###################################################################

recognized = []
strangers = 0

client = mqtt.Client(CLIENT_ID)

#### CALLBACKS ################################################################

def on_connect(client, userdata, flags, rc):
    client.subscribe(ROOT_TOPIC + '/sensors/#')
    client.subscribe(ROOT_TOPIC + '/cameras/pi-cam/#')
    client.subscribe(ROOT_TOPIC + '/preferences/mode')
    
def on_message(client, userdata, message):
    global recognized, strangers

    print(message.topic)
    print(str(message.payload.decode("utf-8")))
    try:
        value = json.loads(str(message.payload.decode("utf-8")))
    except:
        value = str(message.payload.decode("utf-8"))
    path = message.topic.replace(ROOT_TOPIC + '/', '')

    print(f"####  path: {path}, value: {value}, type: {type(value)}\n")

    if (path == "preferences/mode"):  switch2mode(value)

    elif (path == "sensors/flame" and value == True):  act_on_flame()
    elif (path == "sensors/gas" and value == True):  act_on_gas()
    elif (path == "sensors/rain" and value == True):  act_on_rain()
    elif (path == "sensors/pir/state" and value == True):  act_on_pir()

    elif (path == "cameras/pi-cam/recognized"):
        if (value != None): recognized = value
        else: recognized = []
    elif (path == "cameras/pi-cam/strangers"):  strangers = value       
    elif (path == "cameras/pi-cam/notify" and value == True):  notify_door()

#### MAIN() ###################################################################

def main():

    ### Initialization ##############################  
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS)

    ### Loop ########################################
    client.loop_start()

    try:
        while True:
            sleep(0.2)

    except KeyboardInterrupt:
        pass

    client.loop_stop()
    client.disconnect()

#### FUNCTIONS ################################################################

def act_on_flame():
    client.publish(ROOT_TOPIC + "/actuators/alarm", 'true', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/door", 'true', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/gate", 'true', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/window", 'true', retain=False)

def act_on_gas():
    client.publish(ROOT_TOPIC + "/actuators/alarm", 'true', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/door", 'true', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/gate", 'true', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/window", 'true', retain=False)

def act_on_rain():
    client.publish(ROOT_TOPIC + "/actuators/window", 'false', retain=False)

def act_on_pir():
    client.publish(ROOT_TOPIC + "/actuators/door", 'false', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/gate", 'false', retain=False)
    client.publish(ROOT_TOPIC + "/actuators/window", 'false', retain=False)

def notify_door():
    global recognized, strangers
    notification = ""

    if(len(recognized) == 0):
        if(strangers == 1): notification = f"There's a stranger on the door"
        elif(strangers > 1): notification = f"There are {strangers} strangers on the door"

    elif(len(recognized) == 1):
        if(strangers == 0): notification = f"{recognized[0]} is on the door"
        if(strangers == 1): notification = f"{recognized[0]} is on the door with a stranger"
        elif(strangers > 1): notification = f"{recognized[0]} is on the door with {strangers} strangers"

    elif(len(recognized) > 1):
        names = ""
        for i in range(len(recognized)-2):
            names += recognized[i] + ', '
        names += recognized[-2] + ' and ' + recognized[-1]

        if(strangers == 0): notification = f"{names} are on the door"
        elif(strangers == 1): notification = f"{names} are on the door with a stranger"
        elif(strangers > 1): notification = f"{names} are on the door with {strangers} strangers"
    
    client.publish(ROOT_TOPIC + "/cameras/pi-cam/notification", notification, retain=False)


def switch2mode(value):
    if (value == 'day'):
        client.publish(ROOT_TOPIC + "/preferences/mode", 'default', retain=False)
        client.publish(ROOT_TOPIC + "/preferences/speaker/doorbot-enable", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/sensors/pir/enable", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/bedroom/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony1/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony2/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/garage/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/garden/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/hall1/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/kitchen/state", 'false', retain=False)
    elif (value == 'night'):
        client.publish(ROOT_TOPIC + "/preferences/mode", 'default', retain=False)
        client.publish(ROOT_TOPIC + "/preferences/speaker/doorbot-enable", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/sensors/pir/enable", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony1/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony2/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/bedroom/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/garage/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/garden/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/hall1/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/kitchen/state", 'true', retain=False)
    elif (value == 'sleep'):
        client.publish(ROOT_TOPIC + "/actuators/door", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/actuators/gate", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/preferences/mode", 'default', retain=False)
        client.publish(ROOT_TOPIC + "/preferences/speaker/doorbot-enable", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/preferences/speaker/reporter-enable", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/sensors/pir/enable", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony1/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/balcony2/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/bedroom/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/garage/state", 'false', retain=False)
        client.publish(ROOT_TOPIC + "/lights/garden/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/hall1/state", 'true', retain=False)
        client.publish(ROOT_TOPIC + "/lights/kitchen/state", 'false', retain=False)

#### EXECUTE ##################################################################

if (__name__ == '__main__'): main()