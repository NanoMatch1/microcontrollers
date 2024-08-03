const int ledPin = 13;       // Example pin for an LED
const int resetPin = 12;     // Pin for resetting the counters
const int lastDigit = 11;    // Pin for reading the last digit of the counters
const int countEnable = 10;  // Pin for gating the MOSFET to allow the TTL signal through to the latch

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  pinMode(resetPin, OUTPUT);
  pinMode(lastDigit, INPUT);
  pinMode(countEnable, OUTPUT);
  Serial.println("Ready to receive commands:");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove any leading/trailing whitespace
    parseInput(input);
  }
}

void parseInput(String input) {
  int spaceIndex = input.indexOf(' ');

  if (spaceIndex == -1) {
    Serial.println("Error: Invalid input format. Use <command> <value>.");
    return;
  }

  String command = input.substring(0, spaceIndex);
  String valueStr = input.substring(spaceIndex + 1);
  float value = valueStr.toFloat();

  performCommand(command, value);
}

int readCounts() {
  // Implement the logic to read the counts here
  // For demonstration purposes, returning a dummy count value
  return analogRead(lastDigit); // Example of reading a value
}

int acquireData(float acquisitionTime) {
  digitalWrite(countEnable, HIGH);
  
  unsigned long startTime = micros();
  unsigned long waitTime = startTime + (unsigned long)(acquisitionTime * 1000000);
  
  while (micros() < waitTime) {
    // Busy-waiting for the acquisition time to elapse
  }

  digitalWrite(countEnable, LOW);
  
  unsigned long endTime = micros();
  int counts = readCounts(); // Edit this to read counts

  unsigned long elapsedTime = endTime - startTime;
  Serial.print("Elapsed time: ");
  Serial.print(elapsedTime);
  Serial.println(" us");

  return counts;
}

void performCommand(String command, float value) {
  if (command == "t") {
    int counts = acquireData(value);
    Serial.print("Counts: ");
    Serial.println(counts);
  } else {
    Serial.println("Error: Unknown command.");
  }
}
