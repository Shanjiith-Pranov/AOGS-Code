#include <Tsensors.h>
#include <Wire.h>
#include <avr/wdt.h>
#include <WISOL.h>


int initialWaveStart;
float timediff;
int currentWave = 0;
float initialWavethreshold = 2;
float differenceWavethreshold = 0.5;
int timer = millis();
float prevXAccel;
float prevYAccel;
float prevZAccel;
uint8_t PublicModeSF;
Tsensors *tSensors = new Tsensors();
Isigfox *Isigfox = new WISOL();


void getDLMsg(){
  recvMsg *RecvMsg;
  int result;

  RecvMsg = (recvMsg *)malloc(sizeof(recvMsg));
  result = Isigfox->getdownlinkMsg(RecvMsg);
  for (int i=0; i<RecvMsg->len; i++){
    Serial.print(RecvMsg->inData[i]);
  }
  Serial.println("");
  free(RecvMsg);
}


void Send_Pload(uint8_t *sendData, const uint8_t len){
  // No downlink message require
  recvMsg *RecvMsg;

  RecvMsg = (recvMsg *)malloc(sizeof(recvMsg));
  Isigfox->sendPayload(sendData, len, 0, RecvMsg);
  for (int i = 0; i < RecvMsg->len; i++) {
    Serial.print(RecvMsg->inData[i]);
  }
  Serial.println("");
  free(RecvMsg);
}


void GetDeviceID(){
  recvMsg *RecvMsg;
  const char msg[] = "AT$I=10";

  RecvMsg = (recvMsg *)malloc(sizeof(recvMsg));
  Isigfox->sendMessage(msg, 7, RecvMsg);

  Serial.print("Device ID: ");
  for (int i=0; i<RecvMsg->len; i++){
    Serial.print(RecvMsg->inData[i]);
  }
  Serial.println("");
  free(RecvMsg);
}
void setup() {
  int flagInit;
  tSensors->initSensors();
  Serial.begin(9600);
  PublicModeSF = 0;
  flagInit = Isigfox->initSigfox();
  Isigfox->testComms();
  GetDeviceID();
  flagInit = -1;
  while (flagInit == -1) {
  Serial.println(""); // Make a clean restart
  delay(1000);
  PublicModeSF = 0;
  flagInit = Isigfox->initSigfox();
  Isigfox->testComms();
  GetDeviceID();
  Wire.begin();
  Wire.setClock(100000);
  }
}
void loop() {
  Serial.println("");
  prevXAccel = tSensors->getAccX();
  prevYAccel = tSensors->getAccY();
  prevZAccel = tSensors->getAccZ();
  Serial.print("Acc X: "); Serial.println(tSensors->getAccX());
  Serial.print("Acc Y: "); Serial.println(tSensors->getAccY());
  Serial.print("Acc Z: "); Serial.println(tSensors->getAccZ());
  if (currentWave = 0) {
    if (tSensors->getAccX() > initialWavethreshold) {
      initialWaveStart = millis();
      currentWave = 1;
    }
    else if (tSensors->getAccY() > initialWavethreshold) {
      initialWaveStart = millis();
      currentWave = 1;
    } else if (tSensors->getAccZ() > initialWavethreshold) {
      initialWaveStart = millis();
      currentWave = 1;
    }
  } else if (currentWave = 1) {
    if (tSensors->getAccX() - prevXAccel > differenceWavethreshold){
    timediff = timer - initialWaveStart;
    timediff = timediff/1000;
    Send_Pload((const char*)&timediff, sizeof(timediff));
    delay(20000);
  } else if (tSensors->getAccY() - prevYAccel > differenceWavethreshold){
    timediff = timer - initialWaveStart;
    timediff = timediff/1000;
    Send_Pload((const char*)&timediff, sizeof(timediff));
    delay(20000);
  } else if (tSensors->getAccZ() - prevZAccel > differenceWavethreshold){
    timediff = timer - initialWaveStart;
    timediff = timediff/1000;
    Send_Pload((const char*)&timediff, sizeof(timediff));
    delay(20000);
  }
}
}