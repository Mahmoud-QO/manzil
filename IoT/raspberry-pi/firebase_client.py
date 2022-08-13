import json
import pyrebase
import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
from time import sleep

#### DEFINE ###################################################################

CLIENT_ID = 'SMART-HOME-FIREBASE-CLIENT'
BROKER_ADDRESS = 'localhost'
ROOT_TOPIC = 'mqtt/smart-home/v0'

email = "1100@smarthome.com"
password = "123456"

config = {
    "apiKey": "AIzaSyD69jD4HB-v9tHr1V5SCxUfIyRTKr8N2OI",
    "authDomain": "smart-home-zu022.firebaseapp.com",
    "databaseURL": "https://smart-home-zu022-default-rtdb.firebaseio.com",
    "projectId": "smart-home-zu022",
    "storageBucket": "smart-home-zu022.appspot.com",
    "messagingSenderId": "642702441003",
    "appId": "1:642702441003:web:3173b342845df608a7c86e",
    "measurementId": "G-XM0W7LPX79"
}

#### GLOBAL ###################################################################

uid = "/"

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

client = mqtt.Client(CLIENT_ID, protocol=mqtt.MQTTv5)

#### CALLBACKS ################################################################

## Firebase ##
#
def stream_handler(message):
    # TODO fix the error when a path is deleted from Firebese

    if(message['path'] != '/'):
        value = json.dumps(message['data'])

        client.publish(ROOT_TOPIC + message['path'], value, retain=False)

        print(f"####  topic: {message['path']}, value: {value}, type: {type(value)}, original: {type(message['data'])}\n")

## MQTT ##
#
def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe((ROOT_TOPIC + '/#', SubscribeOptions(noLocal=True)))

def on_message(client, userdata, message):
    key = message.topic
    key = key.replace(ROOT_TOPIC, uid)
    try:
        value = json.loads(str(message.payload.decode("utf-8")))
    except:
        value = str(message.payload.decode("utf-8"))
          
    path = message.topic.replace(ROOT_TOPIC + '/', '')

    if (path == "cameras/pi-cam/photo" and value == False):
        storage.child("images/pi-cam.jpg").put("images/pi-cam.jpg")

    db.child(key).set(value)
    print(f">>>>  key: {key}, value: {value}, type: {type(value)}\n")

    if (path == "cameras/pi-cam/notify" and value == True):
        db.child(key).set(False)
        storage.child("images/door-notify.jpg").put("images/door-notify.jpg")
        client.publish(ROOT_TOPIC + "/cameras/pi-cam/notify", 'false', retain=False)

    
#### MAIN() ###################################################################
def main():
    global uid

    ### Initialization ##############################

    client.on_message = on_message
    client.on_connect = on_connect

    #### Authentication #############################

    ## Login ##
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        uid = user['localId']
        print("uid: " + uid)
        print("logged in successfully!")

        db.child(uid).stream(stream_handler)    # set Firebase data change listener
        client.connect(BROKER_ADDRESS)          # connect to the MQTT broker   
    except:
        print("Invalid email or password.")

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

# millis = lambda: int(round(time() * 1000))

#### EXECUTE ##################################################################

if (__name__ == '__main__'): main()
