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

void setup() {
  tSensors->initSensors();
  Serial.begin(9600);
  PublicModeSF = 0;
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
  } else if (tSensors->getAccY() - prevYAccel > differenceWavethreshold){
    timediff = timer - initialWaveStart;
    timediff = timediff/1000;
  } else if (tSensors->getAccZ() - prevZAccel > differenceWavethreshold){
    timediff = timer - initialWaveStart;
    timediff = timediff/1000;
  }
}
}