/**
    An ESP32 Capacitive touch sensor using touchRead. Upon touch activation (or close hovering)
    the vibration motor is triggered as haptic feedback. The motot should be tapes to the tip of one's
    finger that is approaching the capacitive sensor electrode for the best effect.z
      
    SENSE: GPIO Pin used to detect the voltage
    * Pins:

    - Capacitive SENSE: GPIO_4
    - L239D Enable A: GPIO_13
    - L239D in1: GPIO_12
    - L239D in2: GPIO_14
*/

#include "CalibratedAverageTouchSensor.h"

// Params
#define TOUCH_DEVIATION 5 // this value may depend on the object and the person touching it, you should tune it
#define TOUCH_CALIBRATION_NUM_SAMPLES 30  // number of samples in calibration
#define TOUCH_CALIBRATION_DELAY_MS 20     // delay used between samples in calibration
#define TOUCH_READ_DELAY_MS 20 // delay used for the main "loop"

uint32_t touchActivationThreshold = 100;  // Adjust this after observing the serial output during touches
uint32_t hapticActivationSpeed = 80; // Value between 0->255 for speed, 0 is off, 255 is max

// Capacitive Pins
const int SENSE_PIN = 4; // 18;
CalibratedAverageTouchSensor touchSensor1 = CalibratedAverageTouchSensor(SENSE_PIN, TOUCH_DEVIATION);

// Motor Pins
const int enA = 13;
const int in1 = 12;
const int in2 = 14;

// The current motor speed
long currentMotorSpeed = 0;

void setup() {
  Serial.begin(115200);
  initCapacitiveSensor();
  initMotor();

}

void initCapacitiveSensor() {
  Serial.println("Init Cap sensor");
  // T1
  touchSensor1.calibrate(TOUCH_CALIBRATION_NUM_SAMPLES, TOUCH_CALIBRATION_DELAY_MS);
  Serial.print("T1 Average: ");
  Serial.println(touchSensor1.getAverage());
  
  Serial.println("Calibration Done.");
  delay(200);
}

void initMotor() {
  // Set all the pins as outputs
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  // Turn off the motor to start with
  stopMotor();
}

// Main loop
void loop() {
  bool isTouched = touchSensor1.isTouched(); //touchRead(SENSE_PIN); //.touch();//readSensor();
  if (isTouched) {
    Serial.println("  TOUCH");
    currentMotorSpeed = hapticActivationSpeed;
    setMotorDirForward();
    startMotorWithSpeed(currentMotorSpeed);
  } else {
    Serial.println("  no touch");
    stopMotor();
  }
  delay(TOUCH_READ_DELAY_MS);
}

/////////////////////////
// Motor Functionality //
/////////////////////////
void setMotorDirForward() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
}

void setMotorDirBack() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
}

void stopMotor() {
  digitalWrite(enA, LOW);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
}

void startMotor() {
  digitalWrite(enA, HIGH);
}

void startMotorWithSpeed(int speed) {
  analogWrite(enA, speed);
}