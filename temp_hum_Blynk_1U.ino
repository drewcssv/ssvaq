/**************************************************************
 Simple Blynk Sketch to monitor internal temp and humidity of power/comms sensor support boxes
 *Author: A. L. Clark, SSV
 * 
 *   DHT22 ----gpio2
 *
 **************************  BOX 1U  ********************************/

#define BLYNK_PRINT Serial    // Comment this out to disable prints and save space
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <SimpleTimer.h>
#include <DHT.h>
#define DHTPIN 2 //pin gpio 12 in sensor
#define DHTTYPE DHT22   // DHT 22 Change this if you have a DHT11
#define LENG 31  //0x42 + 31 bytes equal to 32 bytes  
DHT dht(D2, DHTTYPE);

char auth[] = "6b7534b767b940db897c401f8064ab2c";  // Put your Auth Token here. (see Step 3 above)

char ssid[] = "T-Mobile Broadband 10";  // SSV Radio on Gateway Two array
char pass[] = "Rivadog17"; // SSV

unsigned char buf[LENG];  
char floatString[15];
char buffer[20];
float temp, hum ;

SimpleTimer timer;

void setup()
{
  Serial.begin(9600); // See the connection status in Serial Monitor
   Blynk.begin(auth, ssid, pass, "blynk-cloud.com", 80);
 
  // Setup a function to be called every 10 seconds
  timer.setInterval(10000L, sendUptime);
}

void sendUptime()
{
  // You can send any value at any time.
  // Please don't send more that 10 values per second.
   //Read the Temp and Humidity from DHT
   
  float h = dht.readHumidity();
  float t = dht.readTemperature();
    
// check for valid data 
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    delay(1000);
    return;
  }
  
  Serial.print("Internet Temperature: ");
  Serial.println(t);
  Serial.print("Relative Humidity: ");
  Serial.println(h);

    // English Units - degrees F
    buffer[0] = '\0';
    dtostrf(t * 1.8 + 32.0, 5, 1, floatString);
    temp = t*1.8 + 32.0;
    strcat(buffer, floatString);
    strcat(buffer, "F");
  
   Blynk.virtualWrite(10, temp); // virtual pin 
   Blynk.virtualWrite(12, temp); // virtual pin 
   
 // English Units - percent % 
    buffer[0] = '\0';
    dtostrf(h, 5, 1, floatString);
    hum = h;
    strcat(buffer, floatString);
    strcat(buffer, "%");
    
   Blynk.virtualWrite(11, hum); // virtual pin 
   Blynk.virtualWrite(13, hum); // virtual pin 
}

void loop()
{
  Blynk.run();
  timer.run();
}
