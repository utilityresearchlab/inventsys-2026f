/**
  An ESP32 Capacitive touch sensor without touchRead
  Touching the electrode increases its capacitance, which
  changes the charge/discharge time.
             
  CHARGE Pin ----> Resistor (1Mohm) ----+----> SENSE Pin
                                        |
                                        v
                                      electrode 
                    
  CHARGE: GPIO Pin used to charge the electrode
  SENSE: GPIO Pin used to detect the voltage
*/

const int CHARGE_PIN = 5;
const int SENSE_PIN  = 18;

const uint32_t TIMEOUT_US = 10000;

// Number of measurements used for averaging
const int SAMPLES = 10;

// Adjust this after observing the serial output during touches
uint32_t touchThreshold = 100;

void setup() {
  Serial.begin(115200);
  pinMode(CHARGE_PIN, OUTPUT);
  digitalWrite(CHARGE_PIN, LOW);

  pinMode(SENSE_PIN, INPUT);
  Serial.println("ESP32 capacitive sensor start");
}

void loop() {
  uint32_t value = readSensor();

  Serial.print("Charge time: ");
  Serial.print(value);
  Serial.print(" us");

  if (value > touchThreshold) {
    Serial.println("  TOUCH");
  }
  else {
    Serial.println("  no touch");
  }
  delay(50);
}

uint32_t measureCapacitance() {
  uint32_t start;
  uint32_t elapsed;

  // Completely discharge the sensor
  pinMode(CHARGE_PIN, OUTPUT);
  digitalWrite(CHARGE_PIN, LOW);

  pinMode(SENSE_PIN, OUTPUT);
  digitalWrite(SENSE_PIN, LOW);

  delayMicroseconds(20);

  // Make SENSE input
  pinMode(SENSE_PIN, INPUT);

  // Start charging.
  digitalWrite(CHARGE_PIN, HIGH);

  start = micros();

  // Wait for SENSE to become HIGH
  while (digitalRead(SENSE_PIN) == LOW) {
    elapsed = micros() - start;
    if (elapsed >= TIMEOUT_US) {
      break;
    }
  }

  // Stop charging
  digitalWrite(CHARGE_PIN, LOW);
  return elapsed;
}

uint32_t readSensor() {
  uint32_t total = 0;

  for (int i = 0; i < SAMPLES; i++) {
    total += measureCapacitance();
  }
  return total / SAMPLES;
}

