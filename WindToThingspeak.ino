// Program to read and parse data from NASA Clipper Wind sensor
// Version 0.8  A.L. Clark  SSV  (c) 2019   WORKING!!
// Set up to use the Adafruit Huzzah Feather ESP8266  microcontroller
#include <SoftwareSerial.h> //using software serial port
#include <nmea.h>
#include "ThingSpeak.h"
#include <ESP8266WiFi.h>
 
static const int RXPin = 13, TXPin = 15; //Adafruit Huzzah
static const uint32_t WINDBaud = 4800; // for the NASA wind sensor 
 
// replace your wifi username and password
const char* ssid     = "T-Mobile Broadband 10"; // or "10" on the other array
const char* password = "xxx"; //SSV password
 
unsigned long myChannelNumber = 746995; //  "Replace it with your thingspeak channel number"
const char * myWriteAPIKey = "write_api_key"; // write API key
 
WiFiClient  client; // start ESP WiFi client
 
SoftwareSerial ss(RXPin, TXPin, false);  // 

NMEA nmeaDecoder(ALL); // start NMEA decoder
 
void setup()
{
  
// The serial connection to the Wind device will use  

  
  ss.begin(WINDBaud); 
  

  Serial.begin(4800); // for console

  //Serial.swap();


  Serial.println(F("Wind sensor writing to Thingspeak"));
  Serial.println();
 
  Serial.print("Connecting to ");
 Serial.println(ssid);
 WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
   Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Netmask: ");
  Serial.println(WiFi.subnetMask());
  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());
  ThingSpeak.begin(client);
  
}
void displayInfo()  // Routine to read, decode and transmit to Thingspeak
{
 if (ss.available()) {  // if we have serial stream
  // Serial.print(ss.read()); // debug
   if (nmeaDecoder.decode(ss.read())) {  // if we get a valid NMEA sentence  
     Serial.println(nmeaDecoder.sentence());  // Looking for MWV - Wind Speed and Angle
     
     char* t0 = nmeaDecoder.term(0);  // $-: Talker identifier
     char* t1 = nmeaDecoder.term(1);  // MWV: Sentence formatter
     char* t2 = nmeaDecoder.term(2);  // x.x: Wind angle, 0 - 359 degrees
     char* t3 = nmeaDecoder.term(3);  // a: Reference, R=relative, T=true
     char* t4 = nmeaDecoder.term(4); //  x.x: Wind speed
     char* t5 = nmeaDecoder.term(5); //  a: Wind speed units, K=km.h, M=m/s, N=knots
     char* t6 = nmeaDecoder.term(6); //  A: Status, A=data valid V=data invalid
     char* t7 = nmeaDecoder.term(7);  // *hh: Checksum
       
     Serial.print("Term 0: ");  
     Serial.println(t0);  
     Serial.print("Term 1: ");  
     Serial.println(t1);  
     Serial.print("Term 2: ");  
     Serial.println(t2);  
     Serial.print("Term 3: ");  
     Serial.println(t3);  
     Serial.print("Term 4: ");  
     Serial.println(t4);  
     Serial.print("Term 5: ");  
     Serial.println(t5);  
     Serial.print("Term 6: ");  
     Serial.println(t6);  
     Serial.print("Term 7: ");  
     Serial.println(t7);  
      
     Serial.println("--------");    
 
    ThingSpeak.setField(1, t0);
   ThingSpeak.setField(2, t1);
    ThingSpeak.setField(3, t2);  // Wind Angle
    ThingSpeak.setField(4, t3);
    ThingSpeak.setField(5, t4);  // Wind Speed
    ThingSpeak.setField(6, t5);
    ThingSpeak.setField(7, t6);  // Data Valid
   ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey); // send to Thingspeak channel
    Serial.println("Thingspeak data written..."); 
    delay(20000);
 }  
} 
  else
  {
    Serial.print(F("INVALID"));
  }
  
}
void loop()
{
  // This sketch sends data to Thingspeak every time a new sentence is correctly encoded.
  
  while (ss.available() > 0) // Loop white data available
       
      displayInfo();
  
}
