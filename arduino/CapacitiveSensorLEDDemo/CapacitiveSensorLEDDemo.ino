#define TOUCH_ACTIVATED_VALUE 500

const int LED_PIN = 27; 
const int TOUCH_PIN = 32; 
int counter = 0;
bool isLEDOn = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  // Serial.print("Hello: ");
  // Serial.println(counter);
  // counter += 1;
  int sensedValue = touchRead(TOUCH_PIN);
  Serial.print("0,2000");
  Serial.print(",");
  Serial.println(sensedValue);
  delay(10);

  if (senseValue <= TOUCH_ACTIVATED_VALUE) {
    // flip LED state
    isLEDOn = !isLEDOn;
  }
  
  // // Toggle LED
  // digitalWrite(LED_PIN, HIGH);
  // delay(100);
  // digitalWrite(LED_PIN, LOW);
  // delay(100);
}
