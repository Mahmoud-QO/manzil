import json
import pyttsx3
import paho.mqtt.client as mqtt
from datetime import datetime
from time import sleep

#### DEFINE ###################################################################

CLIENT_ID = 'SMART-HOME-PI-SPEAKER-CLIENT'
BROKER_ADDRESS = '192.168.1.100'
ROOT_TOPIC = 'mqtt/smart-home/v0'

DAVID = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0'
ZIRA = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'

#### GLOBAL ###################################################################

doorbot_enabled = True
reporter_enabled = True
gender = 'default'

temperature = 0
humidity = 0
weather = 'sunny-day'

flame = False
gas = False
pir = False
rain = False

notify = False
door_notification = ""

engine = pyttsx3.init()
client = mqtt.Client(CLIENT_ID)

#### CALLBACKS ################################################################

def on_connect(client, userdata, flags, rc):
    client.subscribe(ROOT_TOPIC + '/sensors/#')
    client.subscribe(ROOT_TOPIC + '/cameras/pi-cam/#')
    client.subscribe(ROOT_TOPIC + '/preferences/speaker/#')
    
def on_message(client, userdata, message):
    global doorbot_enabled, reporter_enabled, gender
    global temperature, humidity, weather
    global flame, gas, pir, rain
    global notify, door_notification

    print(message.topic)
    print(str(message.payload.decode("utf-8")))
    try:
        value = json.loads(str(message.payload.decode("utf-8")))
    except:
        value = str(message.payload.decode("utf-8"))
    path = message.topic.replace(ROOT_TOPIC + '/', '')

    print(f"####  path: {path}, value: {value}, type: {type(value)}\n")

    if (path == "preferences/speaker/reborter-enable"):  reporter_enabled = value
    elif (path == "preferences/speaker/doorbot-enable"):  doorbot_enabled = value
    elif (path == "preferences/speaker/gender"):  gender = value

    elif (path == "sensors/temperature"):  temperature = value
    elif (path == "sensors/humidity"):  humidity = value
    elif (path == "sensors/weather"):  weather = value

    elif (path == "sensors/flame"):  flame = value
    elif (path == "sensors/gas"):  gas = value
    elif (path == "sensors/pir/state"):  pir = value

    elif (path == "sensors/rain"):  rain = value

    elif (path == "cameras/pi-cam/notification"):  
        door_notification = value
        notify = True

#### MAIN() ###################################################################

def main():
    global doorbot_enabled, reporter_enabled, gender
    global temperature, humidity, weather
    global flame, gas, pir, rain
    global notify, door_notification

    ### Initialization ##############################
    
    engine.setProperty('rate', 150)

    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS)

    ### Loop ########################################
    client.loop_start()

    try:
        while True:
            sleep(0.2)

            if(gender == 'male' or gender == 'default'):  engine.setProperty('voice', DAVID)
            elif(gender == 'female'):  engine.setProperty('voice', ZIRA)

            #### Alarm #############################
            ## alert fire ##
            if(flame):
                print("Fire! Fire! Fire! There's fire at the garage")
                engine.say("Fire! Fire! Fire! There's fire at the garage")
                engine.runAndWait()

            ## alert gas ##
            if(gas):
                print("Gas leakage! Gas leakage! Gas leakage at the kitchen")
                engine.say("Gas leakage! Gas leakage! Gas leakage at the kitchen")
                engine.runAndWait()

            #### Doorbot ##############################
            if(doorbot_enabled and notify):
                print(f"Notice,  {door_notification}")
                engine.say(f"Notice,  {door_notification}")
                engine.runAndWait()
                notify = False
        

            if(gender == 'male'):  engine.setProperty('voice', DAVID)
            elif(gender == 'female' or gender == 'default'):  engine.setProperty('voice', ZIRA)

            #### Rain ##############################
            if(rain):
                print("It's raining! It's raining! Be aware, it's raining")
                engine.say("It's raining! It's raining! Be aware, it's raining")
                engine.runAndWait()
                rain = False


            #### Reporter #############################
            if(reporter_enabled):
                now = datetime.now()
                if(now.strftime('%M') == '00' or  now.strftime('%M') == '08') and (now.strftime('%S') == '00' or  now.strftime('%S') == '30'):

                    ## greet first ##
                    if(int(now.strftime('%H')) >= 5) and (int(now.strftime('%H')) <= 11):
                        print("Good morning")
                        engine.say("Good morning")
                    elif(int(now.strftime('%H')) >= 12) and (int(now.strftime('%H')) <= 15):
                        print("Good afternoon")
                        engine.say("Good afternoon")
                    elif(int(now.strftime('%H')) >= 16) and (int(now.strftime('%H')) <= 19):
                        print("Good evening")
                        engine.say("Good evening")
                    elif(int(now.strftime('%H')) >= 20) or (int(now.strftime('%H')) <= 4):
                        print("Good night")
                        engine.say("Good night")
                    engine.runAndWait()

                    ## report time ##
                    print(f"It's {now.strftime('%I:%M %p')}")
                    engine.say(f"It's {now.strftime('%I:%M %p')}")
                    engine.runAndWait()

                    ## report date ##
                    print(now.strftime('%A %B %d'))
                    engine.say(now.strftime('%A %B %d'))
                    engine.runAndWait()

                    ## report temperature ##
                    print(f"Temperature is {temperature} degree")
                    engine.say(f"Temperature is {temperature} degree")
                    engine.runAndWait()

                    ## report humidity ##
                    print(f"Humidity percentage is {humidity}")
                    engine.say(f"Humidity percentage is {humidity}")
                    engine.runAndWait()

    except KeyboardInterrupt:
        pass

    client.loop_stop()
    client.disconnect()

#### FUNCTIONS ################################################################


#### EXECUTE ##################################################################

if (__name__ == '__main__'):  main()

