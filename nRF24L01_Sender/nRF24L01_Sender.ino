#include <SPI.h>
#include <RF24.h>

RF24 radio(7, 8); //指定 Arduino Nano 腳位對應 nRF24L01 之 (CE, CSN)
const byte address[6] = "65841";  //節點位址為 5 bytes + \0=6 bytes
int silent_count = 0;

void setup() {
  Serial.begin(9600);
  radio.begin();  //初始化 nRF24L01 模組
  radio.openWritingPipe(address);  //開啟寫入管線
  radio.setPALevel(RF24_PA_MAX);   //設為低功率, 預設為 RF24_PA_MAX
  radio.stopListening();  //傳送端不需接收, 停止傾聽  // put your setup code here, to run once:
  silent_count = 0;
}

void loop() {
  int v1,v2,v3,v4;
  const char text[12];

  v1 = map(analogRead(A2), 0, 1024, 0,99);
  v2 = map(analogRead(A3), 0, 1024, 0,99);
  v3 = map(analogRead(A4), 0, 1024, 0,99);
  v4 = map(analogRead(A5), 0, 1024, 0,99);
  sprintf(text, "%d,%d,%d,%d", v1, v2, v3, v4);

  if(v1 == 0 && v2 == 0 && v3 == 0 && v4 == 0){
    ++silent_count;
    if(silent_count > 10){
      silent_count = 0;
      Serial.println(text);  
      radio.write(&text, sizeof(text));   //將字串寫入傳送緩衝器
    }
  }else{
    silent_count = 10;
    Serial.println(text);
    radio.write(&text, sizeof(text));   //將字串寫入傳送緩衝器
  }
  delay(1000);
}
