// Turns an LED on when a capacitve sensor is touched
// Maintains the state until the touch is ended and a new touch
// is performed

// touch value for the capacitive sensor 
#define TOUCH_ACTIVATED_VALUE 500

const int TOUCH_PIN = 32; 
const int LED_PIN = 27; 

bool wasSensorTouched = false;
bool isLEDOn = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  int sensedValue = touchRead(TOUCH_PIN);
  bool isCurrentlyTouched = (sensedValue <= TOUCH_ACTIVATED_VALUE) ? true : false;
  // If the sensor is touched, and it was previously not touched
  if (isCurrentlyTouched && wasSensorTouched != isCurrentlyTouched) {
    // Update the touch state
    wasSensorTouched = isCurrentlyTouched;
    
    // Toggle LED state
    isLEDOn = !isLEDOn;
  }

  // Update LED 
  digitalWrite(LED_PIN, (isLEDOn) ? HIGH : LOW);

  // Print state
  Serial.print("0,2000");
  Serial.print(",");
  Serial.println(sensedValue);
  delay(10);
}
