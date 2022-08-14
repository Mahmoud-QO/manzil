#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ezButton.h>
#include <DHT.h>
#include <LiquidCrystal.h>
#include <Keypad.h>

#include "DataHandler.h"
#include "FliPush.h"

//// DEFINE ////////////////////////////////////////////////////////////////////////////////
// Define PCA9685 Constants
#define MIN_PULSE_WIDTH       650
#define MAX_PULSE_WIDTH       2350
#define FREQUENCY             50

// Define Keypad constants
#define ROW_NUM 4
#define COLUMN_NUM 4
char keys[ROW_NUM][COLUMN_NUM] = {
  {'1','2','3', 'A'},
  {'4','5','6', 'B'},
  {'7','8','9', 'C'},
  {'*','0','#', 'D'}
};
byte pin_rows[ROW_NUM] = {48, 47, 46, 45}; //connect to the row pinouts of the keypad
byte pin_column[COLUMN_NUM] = {44, 43, 42, 41}; //connect to the column pinouts of the keypad

// Define Pins on PCA9685 board
#define HALL1_LED 0
#define KITCHEN_LED 1
#define GARAGE_LED 2
#define BEDROOM_LED 3
#define BALCONY_LED 4
#define BALCONY1_LED 5
#define BALCONY2_LED 6

#define CURTAIN_SERVO 7
#define WINDOW_SERVO 8
#define GATE_SERVO 9
#define ESP_CAM_SERVO 10

#define ALARM_LED1 11
#define ALARM_LED2 12

// Define Pins on Arduino Mega
//Sensors
#define FLAME_SENSOR A0
#define GAS_SENSOR A1
#define LDR_SENSOR A2
#define RAIN_SENSOR A3
#define PIR_SENSOR 28
#define DHTPIN 29
#define DHTTYPE DHT11

//Actuators
#define GARDEN_LED_R1 2
#define GARDEN_LED_G1 3
#define GARDEN_LED_B1 4
#define GARDEN_LED_R2 5
#define GARDEN_LED_G2 6
#define GARDEN_LED_B2 7

#define SOLENOID 30
#define FAN 31
#define BUZZER 32

//Define switches
#define HALL1_BTN 33
#define KITCHEN_BTN 34
#define GARAGE_BTN 35
#define BEDROOM_BTN 36
#define BALCONY_BTN 37
#define BALCONY1_BTN 38
#define BALCONY2_BTN 39

// LCD pins <--> Arduino pins
#define RS_LCD1 22
#define EN_LCD1 23
#define D4_LCD1 24
#define D5_LCD1 25
#define D6_LCD1 26
#define D7_LCD1 27
//// GLOBAL ///////////////////////////////////////////////////////
bool flameEnable;
bool gasEnable;
bool ldrEnable;
bool rainEnable;
bool pirEnable;
bool alarmState;

FliPush hall1FP, kitchenFP, garageFP, bedroomFP, balconyFP, balcony1FP, balcony2FP;

bool passwordEntered;
String password;

unsigned long previousMillis;
int pwmAlarmLedsValue;
bool pwmAlarmLedsUp;

unsigned long elapsedMillis;

// Virtual //
/*VirtualSensor temperatureSensor(10, 30, 1, 10), humiditySensor(60, 80, 1, 10), curtain(0, 10, 5, 50); 
VirtualSwitch flameSensor(500), gasSensor(400), ldrSensor(100), pirSensor(300), rainSensor(200);
VirtualSwitch gardenSwitch(50), garageSwitch(50), kitchenSwitch(30), balconySwitch(100), hallSwitch(20), bedroomSwitch(30);
VirtualSwitch window(50), gate(40), door(30), fand(30);*/

// DataHandler //
DataHandler temperatureHandler, humidityHandler, curtainHandler;
DataHandler flameHandler, gasHandler, ldrHandler, pirHandler, rainHandler;
DataHandler gardenHandler, garageHandler, kitchenHandler, balcony1Handler, balcony2Handler, hall1Handler, bedroomHandler;
DataHandler windowHandler, gateHandler, doorHandler, fanHandler, keypadHandler;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

ezButton alarm_switch(40);

DHT dht(DHTPIN,DHTTYPE);

Keypad keypad = Keypad( makeKeymap(keys), pin_rows, pin_column, ROW_NUM, COLUMN_NUM );

LiquidCrystal lcd(RS_LCD1, EN_LCD1, D4_LCD1, D5_LCD1, D6_LCD1, D7_LCD1);
//// SETUP ////////////////////////////////////////////////////////
void setup() {
  Serial.begin(9600);
  pinMode(HALL1_BTN, INPUT);
  pinMode(KITCHEN_BTN, INPUT);
  pinMode(GARAGE_BTN, INPUT);
  pinMode(BEDROOM_BTN, INPUT);
  pinMode(BALCONY_BTN, INPUT);
  pinMode(BALCONY1_BTN, INPUT);
  pinMode(BALCONY2_BTN, INPUT);
  
  pinMode(GARDEN_LED_R1, OUTPUT);
  pinMode(GARDEN_LED_G1, OUTPUT);
  pinMode(GARDEN_LED_B1, OUTPUT);
  pinMode(GARDEN_LED_R2, OUTPUT);
  pinMode(GARDEN_LED_G2, OUTPUT);
  pinMode(GARDEN_LED_B2, OUTPUT);
  pinMode (SOLENOID, OUTPUT);
  pinMode (FAN, OUTPUT);
  pinMode (BUZZER, OUTPUT);
  pinMode (PIR_SENSOR, INPUT);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);
  dht.begin();
  alarm_switch.setDebounceTime(50);
  lcd.begin(16, 2);
  lcd.clear();
  password.reserve(32); // maximum input characters is 33, change if needed
}

//// LOOP /////////////////////////////////////////////////////////
void loop() {
  alarm_switch.loop();
  
  // transmit data to Raspberry Pi
  // 
  temperatureHandler.transmit("sensors/temperature", dht.readTemperature());
  humidityHandler.transmit("sensors/humidity", dht.readHumidity());
  
  if(flameEnable){ flameHandler.transmit("sensors/flame", getBool(analogRead(FLAME_SENSOR), 300, false)); }
  if(gasEnable){ gasHandler.transmit("sensors/gas", getBool(analogRead(GAS_SENSOR), 400, true)); }
  if(ldrEnable){ ldrHandler.transmit("sensors/ldr", getBool(analogRead(LDR_SENSOR), 800, false)); }
  if(rainEnable){ rainHandler.transmit("sensors/rain", getBool(analogRead(RAIN_SENSOR), 350, false)); }
  if(pirEnable){ pirHandler.transmit("sensors/pir/state", getBool(digitalRead(PIR_SENSOR), 1, true)); }

  hall1Handler.transmit("lights/hall1/state", hall1FP.getValue(HALL1_BTN));
  kitchenHandler.transmit("lights/kitchen/state", kitchenFP.getValue(KITCHEN_BTN));
  garageHandler.transmit("lights/garage/state", garageFP.getValue(GARAGE_BTN));
  bedroomHandler.transmit("lights/bedroom/state", bedroomFP.getValue(BEDROOM_BTN));
  gardenHandler.transmit("lights/balcony/state", balconyFP.getValue(BALCONY_BTN));
  balcony1Handler.transmit("lights/balcony1/state", balcony1FP.getValue(BALCONY1_BTN));
  balcony2Handler.transmit("lights/balcony2/state", balcony2FP.getValue(BALCONY2_BTN));
  

  if(passwordEntered){ 
    keypadHandler.transmit("sensors/keypad", password); 
    passwordEntered = false;
    password = "";
  }
  
  // receive data from Raspberry Pi
  //
  String line;
  if (Serial.available()) { line = Serial.readStringUntil('\n'); }
  if (line[0] == '{') {
    StaticJsonDocument<100> doc;
    DeserializationError error = deserializeJson(doc, line);
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }

    if (doc["path"] == "lights/hall1/state") {
      usePCA(HALL1_LED, doc["value"] ? 15000 : 0);
    }
    else if (doc["path"] == "lights/kitchen/state") {
      usePCA(KITCHEN_LED, doc["value"] ? 15000 : 0);
    }
    else if (doc["path"] == "lights/garage/state") {
      usePCA(GARAGE_LED, doc["value"] ? 15000 : 0);
    }
    else if (doc["path"] == "lights/bedroom/state") {
      usePCA(BEDROOM_LED, doc["value"] ? 15000 : 0);
    }
    else if (doc["path"] == "lights/balcony/state") {
      usePCA(BALCONY_LED, doc["value"] ? 15000 : 0);
    }
    else if (doc["path"] == "lights/balcony1/state") {
      usePCA(BALCONY1_LED, doc["value"] ? 15000 : 0);
    }
    else if (doc["path"] == "lights/balcony2/state") {
      usePCA(BALCONY2_LED, doc["value"] ? 15000 : 0);
    }

    else if (doc["path"] == "lights/garden/state") {
      bool value = doc["value"];
      digitalWrite(GARDEN_LED_R1, value); 
      digitalWrite(GARDEN_LED_G1, value);
      digitalWrite(GARDEN_LED_B1, value); 
      digitalWrite(GARDEN_LED_R2, value); 
      digitalWrite(GARDEN_LED_G2, value);
      digitalWrite(GARDEN_LED_B2, value);
    }
    else if (doc["path"] == "lights/garden/rgb"){
      byte r = doc["value"][0];  byte g = doc["value"][1];  byte b = doc["value"][2];
      analogWrite(GARDEN_LED_R1, r);  analogWrite(GARDEN_LED_G1, g);  analogWrite(GARDEN_LED_B1, b);
      analogWrite(GARDEN_LED_R2, r);  analogWrite(GARDEN_LED_G2, g);  analogWrite(GARDEN_LED_B2, b);
    }
 
    else if (doc["path"] == "lights/hall1/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(HALL1_LED, intensity_val);
    }
    else if (doc["path"] == "lights/kitchen/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(KITCHEN_LED, intensity_val);
    }
    else if (doc["path"] == "lights/garage/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(GARAGE_LED, intensity_val);
    }
    else if (doc["path"] == "lights/bedroom/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(BEDROOM_LED, intensity_val);
    }
    else if (doc["path"] == "lights/balcony/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(BALCONY_LED, intensity_val);
    }
    else if (doc["path"] == "lights/balcony1/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(BALCONY1_LED, intensity_val);
    }
    else if (doc["path"] == "lights/balcony2/intensity") {
      int intensity_val = map(doc["value"],0,100,0,15000);
      usePCA(BALCONY2_LED, intensity_val);
    }

    else if (doc["path"] == "actuators/window") {
      usePCA(WINDOW_SERVO, doc["value"] ? MAX_PULSE_WIDTH : MIN_PULSE_WIDTH);
    }
    else if (doc["path"] == "actuators/curtain") {
      int pulse = map(doc["value"],0,100,MIN_PULSE_WIDTH,MAX_PULSE_WIDTH);
      usePCA(CURTAIN_SERVO, pulse);
    }
    else if (doc["path"] == "actuators/gate") {
      usePCA(GATE_SERVO, doc["value"] ? MIN_PULSE_WIDTH : MAX_PULSE_WIDTH);  
    }
    else if (doc["path"] == "cameras/esp-cam/angle") {
      int degree = doc["value"];
      degree = degree + 90;
      int pulse = map(degree,0,180,MIN_PULSE_WIDTH,MAX_PULSE_WIDTH);
      usePCA(ESP_CAM_SERVO, pulse);
      /*signed int degree = doc["value"];
      if(degree <= 45 && degree >= -45){
        degree = -1*degree + 90;  
      }*/
    }

    else if (doc["path"] == "actuators/fan") { digitalWrite(FAN, doc["value"]); }

    else if (doc["path"] == "actuators/door") { digitalWrite(SOLENOID, !doc["value"]); }

    else if (doc["path"] == "actuators/lcd") { doc["value"] ? lcd.display() : lcd.noDisplay(); }

    else if (doc["path"] == "actuators/alarm") {
      alarmState = doc["value"];
    }
    
    else if(doc["path"] == "sensors/pir/enable"){
      pirEnable = doc["value"];
    }
    else if(doc["path"] == "sensors/flame/enable"){
      flameEnable = doc["value"];
    }
    else if(doc["path"] == "sensors/gas/enable"){
      gasEnable = doc["value"];
    }
    else if(doc["path"] == "sensors/ldr/enable"){
      ldrEnable = doc["value"];
    }
    else if(doc["path"] == "sensors/rain/enable"){
      rainEnable = doc["value"];
    }
  }
  actOnAlarm();
  getPassword();
  disableAlarm();
  showTemperature();
}  


//// FUNCTIONS ////////////////////////////////////////////////////
void usePCA(byte servoName, int pulse){
  int pulse_width;
  pulse_width = int(float(pulse) / 1000000 * FREQUENCY * 4096);
  pwm.setPWM(servoName, 0, pulse_width);
}
bool getBool(int sensorValue, int threeshold, bool bias){
  bool boolValue;
  if(bias){
    (sensorValue >= threeshold) ? boolValue = true : boolValue = false;
  }else{    
    (sensorValue <= threeshold) ? boolValue = true : boolValue = false;
  }
  return boolValue;
}

void getPassword(){
  char key = keypad.getKey();

  if (key){
    if(key == '*') {
      password = ""; // reset the input password
    }else if(key == '#') {
      passwordEntered = true;
    }else {
      password += key; // append new characteur to input password string
    }
  }
}

void actOnAlarm(){
  if(alarmState == true){
    if (millis() - previousMillis > 10) {
      previousMillis = millis();
      if(pwmAlarmLedsValue >= 15000 ) { 
        pwmAlarmLedsUp = false;
        noTone(BUZZER); 
      }
      else if(pwmAlarmLedsValue <= 0){
        pwmAlarmLedsUp = true;
        tone(BUZZER, 1000);
      }

      if(pwmAlarmLedsUp) pwmAlarmLedsValue += 100;
      else pwmAlarmLedsValue -= 100;
      usePCA(ALARM_LED1, pwmAlarmLedsValue);
      usePCA(ALARM_LED2, pwmAlarmLedsValue);
      
    }
  }else{
    noTone(BUZZER);
    usePCA(ALARM_LED1, 0);
    usePCA(ALARM_LED2, 0);
  }
}

void disableAlarm(){
  if(alarm_switch.isPressed()){ alarmState = false; }
}
void showTemperature(){
  if (millis() - elapsedMillis > 5000) {
    elapsedMillis = millis();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(" Temperature is");
    lcd.setCursor(1, 1);
    lcd.print(dht.readTemperature());
    lcd.print((char)223);
    lcd.print("C");
  }
}
///////////////////////////////////////////////////////////////////////////////////
