#ifndef DATA_HANDLER_H
#define DATA_HANDLER_H

#include <ArduinoJson.h>

class DataHandler 
{   
    byte _previousValue;
           
  public:

    // bool input
    void transmit(String path, bool value) { 
      byte currentValue;
      if(value) { currentValue = HIGH; }     
      else { currentValue = LOW; }
      
      if(_previousValue != currentValue) {
        _previousValue = currentValue;
        StaticJsonDocument<100> doc;
        doc["path"] = path;
        doc["value"] = value;
        serializeJson(doc, Serial);
        Serial.println("");
      }
    }
    
    // byte input
    void transmit(String path, byte value) {      
      if(_previousValue != value) {
        _previousValue = value;
        StaticJsonDocument<100> doc;
        doc["path"] = path;
        doc["value"] = value;
        serializeJson(doc, Serial);
        Serial.println("");
      }
    }
    
    // int input
    void transmit(String path, int value) {      
      if(_previousValue != value) {
        _previousValue = value;
        StaticJsonDocument<100> doc;
        doc["path"] = path;
        doc["value"] = value;
        serializeJson(doc, Serial);
        Serial.println("");
      }
    }

    // float input
    void transmit(String path, float value) {
      byte currentValue = round(value);  
      if(_previousValue != currentValue) {
        _previousValue = currentValue;
        StaticJsonDocument<100> doc;
        doc["path"] = path;
        doc["value"] = value;
        serializeJson(doc, Serial);
        Serial.println("");
      }
    }

    // string input
    void transmit(String path, String value) {
        StaticJsonDocument<100> doc;
        doc["path"] = path;
        doc["value"] = value;
        serializeJson(doc, Serial);
        Serial.println("");
    }
};

#endif

/*
//  public:
//    static const byte FLAME = 1;
//    static const byte GAS = 2;
//    static const byte HUMIDITY = 3;
//    static const byte LDR = 4;
//    static const byte PIR = 5;
//    static const byte RAIN = 6;
//    static const byte TEMPERATURE = 7;
//    
//    SmartSensor(int sensorType) {
//      switch(sensorType) {
//        case FLAME:
//          _sensorType = "flame";
//          break;
//        case GAS:
//          _sensorType = "gas";
//          break;
//        case HUMIDITY:
//          _sensorType = "humidity";
//          break;
//        case LDR:
//          _sensorType = "ldr";
//          break;                    
//        case PIR:
//          _sensorType = "pir";
//          break;         
//        case RAIN:
//          _sensorType = "rain";
//          break;
//        case TEMPERATURE:
//          _sensorType = "temperature";
//          break;
//      }      
//    }
*/
