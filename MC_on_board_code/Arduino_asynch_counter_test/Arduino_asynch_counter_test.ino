// Pin definitions
const int checkPin = 2; // Pin to receive the interrupt signal
const int resetPin = 3;     // Pin to send the reset high signal

// Variables
volatile unsigned long counter = 0; // Counter to increment
float runTime = 0.0;                // Time for the interrupt loop to run
unsigned long startTime = 0;        // Start time for the interrupt loop

void setup() {
  // Initialize pins
  pinMode(checkPin, INPUT); // Set interrupt pin as input
  pinMode(resetPin, OUTPUT);    // Set reset pin as output
  digitalWrite(resetPin, LOW);  // Ensure reset pin is initially LOW

  // Attach interrupt to interruptPin, call handleInterrupt on RISING signal
  // attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterrupt, RISING);

  // Initialize serial communication for debugging
  Serial.begin(9600);
}

// Serial.println("Enter acq time:");

void loop() {
  // Check if serial input is available
  if (Serial.available() > 0) {
    // Read the input as a float
    String command = Serial.readStringUntil('\n');

    Serial.println(command);
    float runTime = command.toFloat();
    Serial.println(runTime);

    // Reset counter and start time
    counter = 0;
    startTime = millis();

    // Reset counter and start time
    counter = 0;
    digitalWrite(resetPin, HIGH);
    // delay(0.001);  // Keep the reset high for a short period
    digitalWrite(resetPin, LOW);
    startTime = millis();
    
    // Run the acquisition loop for the specified time
    while (millis() - startTime < runTime * 1000) {
      // Check the state of the check pin
      if (digitalRead(checkPin) == HIGH) {

        // Send the reset high signal
        digitalWrite(resetPin, HIGH);
        // delay(0.001);  // Keep the reset high for a short period
        digitalWrite(resetPin, LOW);
        // Increment the counter
        counter++;
      }
    }

    // Report the counter value to the serial monitor
    Serial.print("Counter: ");
    Serial.println(counter);
    Serial.println("Enter acquisition time:");
  }
}

// // Interrupt Service Routine (ISR)
// void handleInterrupt() {
//   // Increment the counter
//   counter++;

//   // Send the reset high signal
//   digitalWrite(resetPin, HIGH);
//   delay(0.001);  // Keep the reset high for a short period
//   digitalWrite(resetPin, LOW);
// }
