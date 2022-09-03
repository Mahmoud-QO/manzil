import json
import paho.mqtt.client as mqtt
from time import sleep, time

import face_recognition
import cv2
import pickle
import imutils
from imutils.video import VideoStream
from imutils.video import FPS

#### DEFINE ###################################################################

CLIENT_ID = 'SMART-HOME-PI-CAM-CLIENT'
BROKER_ADDRESS = 'localhost'
ROOT_TOPIC = 'mqtt/smart-home/v0'

encodingsP = "data/encodings.pickle"

#### GLOBAL ###################################################################

client = mqtt.Client(CLIENT_ID)

previous_millis = 0
currentname = "unknown"

password = '123456'
ai_check = False

data = pickle.loads(open(encodingsP, "rb").read())
vs = VideoStream(usePiCamera=True)
fps = FPS()

#### CALLBACKS ################################################################

def on_connect(client, userdata, flags, rc):
    client.subscribe(ROOT_TOPIC + '/#')
    
def on_message(client, userdata, message):
    global password, ai_check

    print(message.topic)
    print(str(message.payload.decode("utf-8")))
    try:
        value = json.loads(str(message.payload.decode("utf-8")))
    except:
        value = str(message.payload.decode("utf-8"))
    path = message.topic.replace(ROOT_TOPIC + '/', '')

    print(f"####  path: {path}, value: {value}, type: {type(value)}\n")
    if (path == "cameras/pi-cam/photo" and value == True):
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        cv2.imwrite("images/pi-cam.jpg",frame)
        client.publish(ROOT_TOPIC + "/cameras/pi-cam/photo", 'false', retain=False)

    elif (path == "sensors/keypad" and value == password):
        ai_check = True
        

#### MAIN() ###################################################################

def main():
    global currentname
    global previous_millis
    global password, ai_check

    ### Initialization ##############################
    vs.start()
    sleep(2)
    fps.start()
    
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS)

    ### Loop ########################################
    client.loop_start()

    try:
        while True:
            sleep(0.2)

            frame = vs.read()
            frame = imutils.resize(frame, width=500)

            cv2.imshow("Facial Recognition is Running", frame)
            
            # cv2.imshow('camera', frame)
            # cv2.imwrite("image.jpg",frame)

            # filename = cv2.imread(r"C:\Users\theki\Desktop\facial_recognition-main\photo/image.jpg")
            # filename = cv2.imread("image.jpg")

            if(millis() - previous_millis > 5000):
                previous_millis = millis()

                filename = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(filename)
                encodings = face_recognition.face_encodings(filename, face_locations)

                names = []
                pepole = []
                ctr = 0

                for encoding in encodings:

                    matches = face_recognition.compare_faces(data["encodings"],encoding,tolerance=0.45)
                    name = "Unknown" 
        
                    if True in matches:      
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}
            
                        for i in matchedIdxs:
                            name = data["names"][i]
                            counts[name] = counts.get(name, 0) + 1
                            
                        name = max(counts, key=counts.get)
                        pepole.append(name)

                            #If someone in your dataset is identified, print their name on the screen
                        if currentname != name:
                            currentname = name
                            
                        # update the list of names
                    names.append(name)
                    
                for((top, right, bottom, left), name) in zip(face_locations, names):
                    cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 225), 2)
                    y= top-15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,.8, (0, 255, 255), 2)
                    
                # cv2.imshow("Facial Recognition is Running", frame)
                # cv2.imwrite("data/pi-cam.jpg",frame)
                            
                for i in range(len(names)):
                    if names[i] == 'Unknown':
                        ctr+=1

                print(names)
                print(pepole)
                print(len(names))
                print(ctr)
                print(millis())
                
                if(len(pepole)> 0 and ai_check == True):
                    client.publish(ROOT_TOPIC + "/actuators/gate", 'true', retain=False)
                    ai_check = False

                elif(len(names) > 0):
                    cv2.imwrite("images/door-notify.jpg",frame)

                    recognized = json.dumps(pepole)
                    client.publish(ROOT_TOPIC + "/cameras/pi-cam/recognized", recognized, retain=False)
                    
                    strangers = json.dumps(ctr)
                    client.publish(ROOT_TOPIC + "/cameras/pi-cam/strangers", strangers, retain=False)
                    
                    client.publish(ROOT_TOPIC + "/cameras/pi-cam/notify", 'true', retain=False)
                    
            k = cv2.waitKey(1)
            if ord('q') == k:
                break

            # update the FPS counter
            fps.update()
            fps.stop()

    except KeyboardInterrupt:
        pass

    client.loop_stop()
    client.disconnect()

    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    vs.stop()


#### FUNCTIONS ################################################################
    
def millis():
    return round(time() * 1000)

#### EXECUTE ##################################################################

if (__name__ == '__main__'): main()