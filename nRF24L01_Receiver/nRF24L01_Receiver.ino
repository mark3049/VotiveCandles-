#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <printf.h>

RF24 radio(7, 8); //指定 Arduino Nano 腳位對應 nRF24L01 之 (CE, CSN)
const byte address[6] = "65841";  //節點位址為 5 bytes + \0=6 bytes

void setup() {
  Serial.begin(9600);
  radio.begin();  //初始化 nRF24L01 模組
  //printf_begin();  //初始化 RF24 的列印輸出功能
  radio.openReadingPipe(0, address);  //開啟 pipe 0 之讀取管線
  radio.setPALevel(RF24_PA_LOW);  //設為低功率, 預設為 RF24_PA_MAX
  radio.startListening();  //接收端開始接收
  //radio.printDetails();  //印出 nRF24L01 詳細狀態
  //Serial.println("NRF24L01 receiver");
  Serial.println("waiting...");
  //delay(1000);
}

char text[32] = "";   //用來儲存接收字元之陣列

void loop() {
if (radio.available()) {  //偵測接收緩衝器是否有資料
    memset(text, 0 ,sizeof(text));
    radio.read(&text, sizeof(text));  //讀取接收字元
    Serial.print(text);
    Serial.print("\r\n");
  }
  if (Serial.available()){    
    String buf = Serial.readString();
    Serial.print(buf);
  }
}
