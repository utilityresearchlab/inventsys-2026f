/*
 * Reads the distance from an HC-SR04 ultrasonic distance sensor, and based on the 
 * DISTANCE_SENSE_MIN and DISTANCE_SENSE_MAX, maps to vibration on a motor using the
 * L239D driver with a 3V3 eccentric rotating mass (ERM) vibration motor.
* Pins:
 *  - HC-SR04 Trigger Pin GPIO_19 
 *  - HC-SR04  Echo Pin GPIO_21 
      THE ECHO NEEDS A VOLTAGE DIVIDE TO DROP 5V to 3V3 for the ESP32
          ECHO -> 1kOhm resistor --> 2k Ohm --> GND
                        |--> GPIO_21
 *  - L239D Enable A: GPIO_13
 *  - L239D in1: GPIO_12
 *  - L239D in2: GPIO_14
 * The default ambient temperature is set to 20C.
 * Dependencies: 
 * 1) HCSR04 library by Martinsos installed via the Libraries menu in 
 * the Arduino IDE. See details of the library here: 
 * https://github.com/Martinsos/arduino-lib-hc-sr04
*/

#include <HCSR04.h>

// Params
#define SENSING_DISTANCE_MIN 0 // millimeters
#define SENSING_DISTANCE_MAX 500 // millimeters
#define SENSING_INTERVAL_MS 50 // milliseconds

// HC-SRC04 Distance Sensor
const int DISTANCE_SENSOR_TRIGGER_PIN = 19;
const int DISTANCE_SENSOR_ECHO_PIN = 21;

// Default value for maximum measurement distance is 4m
UltraSonicDistanceSensor distanceSensor(DISTANCE_SENSOR_TRIGGER_PIN, DISTANCE_SENSOR_ECHO_PIN);
long lastSensorUpdateTime = 0;
float lastSensedDistance = -1;

// Motor connections
const int enA = 13;
const int in1 = 12;
const int in2 = 14;
long currentMotorSpeed = 0;

void setup() {
    Serial.begin(115200);
    initMotor();
}

void initMotor() {
    // Set all the pins as outputs
    pinMode(enA, OUTPUT);
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);   

    // Turn off the motor to start with
    stopMotor();
}

void loop() {
    float currentDistanceMM = getSensedDistanceInMM();
  
    if (currentDistanceMM > SENSING_DISTANCE_MAX || currentDistanceMM < 0) {
        // We're beyond the max distance, so turn the motor off.
        stopMotor();
    } else {
        // Map motor speed to the distance, such that higher speed
        // indicated closer distance
        currentMotorSpeed = round(map(currentDistanceMM, SENSING_DISTANCE_MIN, SENSING_DISTANCE_MAX, 255, 0));
        setMotorDirForward();
        startMotorWithSpeed(currentMotorSpeed);
    }
    Serial.print(currentDistanceMM);
    Serial.print(",");
    Serial.println(currentMotorSpeed);
}

float getSensedDistanceInMM() {
    long currentTime = millis();
    // Only update distance at the specified time interval
    if (currentTime < lastSensorUpdateTime + SENSING_INTERVAL_MS) {
        return lastSensedDistance;
    }
    // Otherwise get a new distance reading and convert to mm
    lastSensedDistance = 10 * distanceSensor.measureDistanceCm();
    lastSensorUpdateTime = currentTime;
    //Serial.println(distance);
    return lastSensedDistance;
}

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