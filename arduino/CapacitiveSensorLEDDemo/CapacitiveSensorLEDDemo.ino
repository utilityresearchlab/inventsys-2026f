#define TOUCH_ACTIVATED_VALUE 500

const int LED_PIN = 27; 
const int TOUCH_PIN = 32; 
int counter = 0;
bool isSensorTouched = false;

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
  
  isSensorTouched = (sensedValue <= TOUCH_ACTIVATED_VALUE) ? true : false;

  // Update LED State
  digitalWrite(LED_PIN, (isSensorTouched) ? HIGH : LOW);
  delay(10);
}
