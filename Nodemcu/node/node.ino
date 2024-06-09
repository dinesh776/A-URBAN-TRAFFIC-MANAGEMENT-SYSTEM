#include <ESP8266WiFi.h>

int port1 = 80;

const char* ssid = "CBlock_Sys_lab";
const char* password = "Rec@cse2023";

const int BUTTON_PIN = D8;
const int LED1_RED = D0;
const int LED1_YELLOW = D1;
const int LED1_GREEN = D2;
const int LED2_RED = D3;
const int LED2_YELLOW = D4;
const int LED2_GREEN = D5;
const int LED_PED_RED = D6;
const int LED_PED_GREEN = D7;
int c=0;

WiFiServer server1(port1);

void setup() {
  pinMode(BUTTON_PIN, INPUT);
  pinMode(LED1_RED, OUTPUT);
  pinMode(LED1_GREEN, OUTPUT);
  pinMode(LED1_YELLOW, OUTPUT);
  pinMode(LED2_RED, OUTPUT);
  pinMode(LED2_GREEN, OUTPUT);
  pinMode(LED2_YELLOW, OUTPUT);
  pinMode(LED_PED_RED, OUTPUT);
  pinMode(LED_PED_GREEN, OUTPUT);

  Serial.begin(115200);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    delay(500);
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print(" on port ");
  Serial.println(port1);

  server1.begin();
  animation();
}

void animation(){
    digitalWrite(LED1_RED, HIGH);
    delay(500);
    digitalWrite(LED1_RED, LOW);
    delay(500);
    digitalWrite(LED1_YELLOW, HIGH);
    delay(500);
    digitalWrite(LED1_YELLOW, LOW);
    delay(500);
    digitalWrite(LED1_GREEN, HIGH);
    delay(500);
    digitalWrite(LED1_GREEN, LOW);
    delay(500);

    digitalWrite(LED2_RED, HIGH);
    delay(500);
    digitalWrite(LED2_RED, LOW);
    delay(500);
    digitalWrite(LED2_YELLOW, HIGH);
    delay(500);
    digitalWrite(LED2_YELLOW, LOW);
    delay(500);
    digitalWrite(LED2_GREEN, HIGH);
    delay(500);
    digitalWrite(LED2_GREEN, LOW);
    delay(500);

    digitalWrite(LED_PED_RED, HIGH);
    delay(500);
    digitalWrite(LED_PED_RED, LOW);
    delay(500);
    digitalWrite(LED_PED_GREEN, HIGH);
    delay(500);
    digitalWrite(LED_PED_GREEN, LOW);
    delay(500);
}


void loop() {
  WiFiClient client1 = server1.available();
  if (client1) {
    Serial.println("Client1 Connected");
    Serial.println(client1.remoteIP().toString());
    animation();
    static unsigned long lastPressTime = 0;
    unsigned long currentMillis = millis();
    while (client1.connected()) {
      int buttonState = digitalRead(BUTTON_PIN);
      static int lastButtonState = LOW; 

      unsigned long currentMillis = millis();
      if(buttonState == HIGH && lastButtonState == LOW) {
        if(currentMillis - lastPressTime > 50) {
          lastPressTime = currentMillis;
          Serial.println("Button Pressed");
          c++;
        }
      }

      lastButtonState = buttonState;
      if (client1.available()) {
        String request = client1.readStringUntil('\n');
        client1.flush();
        Serial.println(request);
        // Split the request into command and value
        int index = request.indexOf(' ');
        String command = request.substring(0, index);
        String value = request.substring(index + 1);

        // Convert the value to an integer
        int delayValue = value.toInt();

        // if (command.equals("4")){
        //   if(c>0){
        //     client1.write("Button Pressed from Nodemcu");
        //     Serial.println("Button Command send to Client");
        //     c=0;
        //   }
        //   else{
        //     client1.write("Button Not pressed from Nodemcu");
        //   }
        // }
        if (command.equals("1")) {
          digitalWrite(LED2_GREEN, LOW);
          digitalWrite(LED1_RED, LOW);
          digitalWrite(LED_PED_GREEN, LOW);
          digitalWrite(LED1_YELLOW, LOW);
          digitalWrite(LED2_YELLOW, LOW);

          digitalWrite(LED1_GREEN, HIGH);
          digitalWrite(LED2_RED, HIGH);
          digitalWrite(LED_PED_RED, HIGH);
          client1.write("ROAD 1 is ON NOW REPLY FROM NODEMCU");
          if(c>0){
            client1.write("Button Pressed from Nodemcu");
            Serial.println("Button Command send to Client");
            c=0;
          }
          else{
            client1.write("Button Not pressed from Nodemcu");
          }
          
          Serial.println("ROAD 1 IS ON NOW");
          delay(delayValue);
        } else if (command.equals("2")) {
          digitalWrite(LED1_GREEN, LOW);
          digitalWrite(LED2_RED, LOW);
          digitalWrite(LED_PED_GREEN, LOW);
          digitalWrite(LED1_YELLOW, LOW);
          digitalWrite(LED2_YELLOW, LOW);

          digitalWrite(LED2_GREEN, HIGH);
          digitalWrite(LED1_RED, HIGH);
          digitalWrite(LED_PED_RED, HIGH);

          client1.write("ROAD 2 is ON NOW REPLY FROM NODEMCU");
          if(c>0){
            client1.write("Button Pressed from Nodemcu");
            Serial.println("Button Command send to Client");
            c=0;
          }
          else{
            client1.write("Button Not pressed from Nodemcu");
          }
          Serial.println("ROAD 2 IS ON NOW");
          delay(delayValue);
        } else if (command.equals("3")) {

          digitalWrite(LED2_GREEN, LOW);
          digitalWrite(LED1_RED, LOW);
          digitalWrite(LED_PED_RED, LOW);
          digitalWrite(LED1_GREEN, LOW);
          digitalWrite(LED2_RED, LOW);

          digitalWrite(LED1_YELLOW, HIGH);
          digitalWrite(LED2_YELLOW, HIGH);
          digitalWrite(LED_PED_GREEN, HIGH);

          client1.write("EQUAL is ON NOW Reply from nodemcu");
          if(c>0){
            client1.write("Button Pressed from Nodemcu");
            Serial.println("Button Command send to Client");
            c=0;
          }
          else{
            client1.write("Button Not pressed from Nodemcu");
          }
          Serial.println("EQUAL IS ON NOW");
          delay(delayValue);
        }
        else if(command.equals("0")){
          digitalWrite(LED2_GREEN, LOW);
          digitalWrite(LED1_RED, LOW);
          digitalWrite(LED_PED_RED, LOW);
          digitalWrite(LED1_GREEN, LOW);
          digitalWrite(LED2_RED, LOW);

          digitalWrite(LED1_YELLOW, LOW);
          digitalWrite(LED2_YELLOW, LOW);
          digitalWrite(LED_PED_GREEN, LOW);
          client1.write("All Leds are OFF from nodemcu");
          if(c>0){
            client1.write("Button Pressed from Nodemcu");
            Serial.println("Button Command send to Client");
            c=0;
          }
          else{
            client1.write("Button Not pressed from Nodemcu");
          }
          Serial.println("All leds are OFF");
          delay(delayValue);

        }
        else if(command.equals("5")){
          digitalWrite(LED2_GREEN, LOW);
          digitalWrite(LED_PED_RED, LOW);
          digitalWrite(LED1_GREEN, LOW);
          digitalWrite(LED1_YELLOW, LOW);
          digitalWrite(LED2_YELLOW, LOW);

          digitalWrite(LED1_RED, HIGH);
          digitalWrite(LED2_RED, HIGH);
          digitalWrite(LED_PED_GREEN, HIGH);
          client1.write("Pedestrian is ON from nodemcu");
          if(c>0){
            client1.write("Button Pressed from Nodemcu");
            Serial.println("Button Command send to Client");
            c=0;
          }
          else{
            client1.write("Button Not pressed from Nodemcu");
          }
          Serial.println("Pedestrian is ON");
          delay(delayValue);

        }
        else if(request != "5" && request != "4" && request != "0" && request != "1" && request != "2" && request != "3"){
          client1.write("INVALID INPUT from NodeMcu");
          if(c>0){
            client1.write("Button Pressed from Nodemcu");
            Serial.println("Button Command send to Client");
            c=0;
          }
          else{
            client1.write("Button Not pressed from Nodemcu");
          }
          Serial.println("INVALID INPUT");
        }

      }
    }
    client1.stop();
    digitalWrite(LED2_GREEN, LOW);
    digitalWrite(LED1_RED, LOW);
    digitalWrite(LED_PED_RED, LOW);
    digitalWrite(LED1_GREEN, LOW);
    digitalWrite(LED2_RED, LOW);

    digitalWrite(LED1_YELLOW, LOW);
    digitalWrite(LED2_YELLOW, LOW);
    digitalWrite(LED_PED_GREEN, LOW);
    Serial.println("Client Disconnected");
    Serial.println("===========================================================");
    Serial.println(" ");
  }
}
