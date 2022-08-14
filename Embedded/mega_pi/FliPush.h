#ifndef FLIPUSH_H
#define FLIPUSH_H

#include <ArduinoJson.h>

/*
 * Instead of using a flip-flop to store the value of a push button and make the push button acts like a switch, these lines of code can do the same function: 
 * Press the push button once   ==> The led turns on
 * Press the push button again  ==> The led turns off
 * Note: the whole program execution time should not exceed 200 ms to work smoothly
 * 
 *   BTN    >>> ___-----_________________-----_________
 *   
 *   x      >>> ___------________________------________
 *   
 *   output >>> ________-----------------------________
 */

class FliPush 
{
    bool _x = false, _output = false;
    
  public:
    
    bool getValue(byte pin) {
      if(digitalRead(pin) == HIGH) { _x = true; }
      if(digitalRead(pin) == LOW && _x){
        _x = false;
        _output = !_output;
      }
      return _output;
    }
};

#endif
