const int BUZZER_PIN = 5; 

void setup() { 
  // Set buzzer to output
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  // play tone for 300 ms, then wait 500 ms
  int frequency = 300;
  tone(BUZZER_PIN, frequency);
  delay(500);
  // Stop sound
  noTone(BUZZER_PIN);
  delay(500);

}
