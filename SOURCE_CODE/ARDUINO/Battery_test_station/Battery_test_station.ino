/*
  Battery Cycling Test
  Created by: Nikola Japundzic
  Date created: 02-28-24
  Last modify date: 07-01-24, Rev 6
  Arduino Nano
 */
#include <Wire.h>

#define TCA_ADDR 0x70    // TCA9548A I2C address
#define INA219_ADDR 0x40 // INA219 I2C address

//RELAYS
//Variables for access of digital outputs for relay controle
    int relay_01 =  A3,
        relay_02 =  9,
        relay_03 =  A2,
        relay_04 =  10,
        relay_05 =  A1,
        relay_06 =  11,
        relay_07 =  A0,
        relay_08 =  12,
        relay_09 =  13,
        relay_10 =  5,
        relay_11 =  2,
        relay_12 =  6,
        relay_13 =  3,
        relay_14 =  7,
        relay_15 =  4,
        relay_16 =  8;
    
//Creating pointer array that points to the addresses of registers that are related to all relay pins
int* digital_relay_array[] = {&relay_01, &relay_02, &relay_03, &relay_04, &relay_05, &relay_06, &relay_07, &relay_08, &relay_09, &relay_10, &relay_11, &relay_12, &relay_13, &relay_14, &relay_15, &relay_16};

                           
void setup() {
  //Serial.begin(115200); // initialize serial communication at 9600 bits per second:
  Serial.begin(250000); // initialize serial communication at 9600 bits per second:
  while (!Serial) {
    delay(10);
  }
  Wire.begin(); // Initialize I2C communication
  // initialize 16 pin's (relay representors) as an output trough the loop:
  for (int i = 0; i < 16; i++) {
    pinMode(*digital_relay_array[i], OUTPUT);    // asigning funcionality OUTPUT to the variable at the *vararray[i] address
    digitalWrite(*digital_relay_array[i], HIGH); // asigning state HIGH to the variable at the *vararray[i] address (High pin = all relays OFF)
  }  
}
void selectChannel(uint8_t channel) {
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}
void loop() {
    get_instruction_from_GUI();
}

String GetStringOfAllDataSeparatedByComma(){
  String Sensors_only = "";
  ///////////////
  for(int i = 0; i <8; i++){
    uint16_t busVoltage_raw, current_raw;
    // Select channel i on the multiplexer
    selectChannel(i);
    Wire.beginTransmission(INA219_ADDR);
    Wire.write(0x02); // Register address for bus voltage
    delay(10);
    Wire.endTransmission(false);
    Wire.requestFrom(INA219_ADDR, (uint8_t)2);
    busVoltage_raw = (Wire.read() << 8) | Wire.read();
    Wire.beginTransmission(INA219_ADDR);
    Wire.write(0x01); // Register address for current
    delay(10);
    Wire.endTransmission(false);
    Wire.requestFrom(INA219_ADDR, (uint8_t)2);
    current_raw = (Wire.read() << 8) | Wire.read();
    // Convert raw values to actual readings
    float busVoltage = (busVoltage_raw >> 3) * 0.004; // LSB = 4mV
    float current = abs((int16_t)current_raw * 0.0001); // LSB = 0.1mA
    float power = busVoltage * current;
    Sensors_only = Sensors_only + String(busVoltage,5) + ",";
    Sensors_only = Sensors_only + String(current,5) + ",";
    Sensors_only = Sensors_only + String(power,5) + ",";
  }

  return Sensors_only;
}
//--------------------------------------------------------------------------------
//Relay controling new ON
void Set_2nd_group_of_relays_ON(){
  for(int i = 0; i < 16; i++){
    digitalWrite(*digital_relay_array[i], LOW); // turn specific relay on:
    i++;
  }
}
void Set_1st_group_of_relays_ON(){
  for(int i = 0; i < 16; i++){
    i++;
    digitalWrite(*digital_relay_array[i], LOW); // turn specific relay on:
  }
}
//Relay controling new OFF
void Set_2nd_group_of_relays_OFF(){
  for(int i = 0; i < 16; i++){
    digitalWrite(*digital_relay_array[i], HIGH); // turn specific relay off:
    i++;
  }
}
void Set_1st_group_of_relays_OFF(){
  for(int i = 0; i < 16; i++){
    i++;
    digitalWrite(*digital_relay_array[i], HIGH); // turn specific relay off:
  }
}
//-------------------------------------------------
#define MAX_MESSAGE_LENGTH 6

void get_instruction_from_GUI() {
  char inByte = ' ';
  while (inByte != '@') {
    while (Serial.available() > 0) {
      // Create a place to hold the incoming message
      static char message[MAX_MESSAGE_LENGTH];
      static unsigned int message_pos = 0;
      // Read the next available byte in the serial receive buffer
      inByte = Serial.read();
      // Message coming in (check not terminating character) and guard for over message size
      if (inByte != '\n' && (message_pos < MAX_MESSAGE_LENGTH - 1)) {
        // Add the incoming byte to our message
        message[message_pos] = inByte;
        message_pos++;
      }
      // Full message received...
      else {
        // Add null character to string
        message[message_pos] = '\0';
        // Print the message (or do other things)
        //Serial.println(message);

        if (strcmp(message, "m") == 0) {
          // "m" = measure and send
          //Serial.println("measure and send");
          Serial.println(GetStringOfAllDataSeparatedByComma());
        }
        else if (strcmp(message, "raon") == 0) {
          // "raon" = relays a on
          Set_1st_group_of_relays_ON();
        }
        else if (strcmp(message, "raoff") == 0) {
          // "raoff" = relays a off
          Set_1st_group_of_relays_OFF();
        }
        //----------------------------------------------
        else if (strcmp(message, "rbon") == 0) {
          // "rbon" = relays b on
          Set_2nd_group_of_relays_ON();
        }
        else if (strcmp(message, "rboff") == 0) {
          // "rboff" = relays b off
          Set_2nd_group_of_relays_OFF();
        }
        else {
          // Not a valid command
          Serial.println("not a valid command");
        }
        /*
        //SEND one of the bottom instructions to the serial for related feedback
        // "m" = measure and send
        // "raon" = relays a on
        // "raoff" = relays a off
        // "rbon" = relays b on
        // "rboff" = relays b off
        */
        // Reset message position for next message
        message_pos = 0;
      }
    }
  }
}