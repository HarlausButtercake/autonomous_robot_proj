#define MIN_SPEED 0
#define MAX_SPEED 255
#define SLOW 50
#define MEDIUM 125
#define FAST 200
#define DEFAULT_DELAY_MS 200



#define IN1  7
#define IN2 6
#define IN3 5
#define IN4 4
#define CHECK 2

volatile char firstChar, secondChar;

void forward(int speed) {
  digitalWrite(IN1, LOW);
  analogWrite(IN2, 255 - speed);
  digitalWrite(IN4, HIGH);
  analogWrite(IN3, speed);
}

void reverse(int speed) {
  digitalWrite(IN1, HIGH);
  analogWrite(IN2, speed);
  digitalWrite(IN4, LOW);
  analogWrite(IN3, 255 - speed);
}

void left(int speed) {
  digitalWrite(IN1, LOW);
  analogWrite(IN2, speed);
  digitalWrite(IN4, HIGH);
  analogWrite(IN3, 255 - speed);
}

void right(int speed) {

}

void halt() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

// void left_reverse(int speed) { //speed: t? 0 - MAX_SPEED
//  speed = constrain(speed, MIN_SPEED, MAX_SPEED);
//  digitalWrite(IN1, LOW);
//  analogWrite(IN2, speed);
// }
int to_int(char c) {
  int k;
  if (c == 'S') {
    k = SLOW;
  } else if (c == 'M') {
    k = MEDIUM;
  } else if (c == 'F') {
    k = FAST;
  } else {
    k = 0;
  }
  return k;
}

void control_main(char c1, char c2) {
  // int speed = to_int(c2);
  int speed = MEDIUM;
//  int speed = 255;
  if (c1 == 'H' || speed == 0) {
    halt();
  } else if (c1 == 'F') {
    forward(speed);
  } else if (c1 == 'B') {
    reverse(speed);
  } else if (c1 == 'L') {
    left(speed);
  } else if (c1 == 'R') {
    right(speed);
  } else {
    
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(CHECK, INPUT);
  halt();
}

void loop() {
  // forward(MEDIUM);
  if (Serial.available() >= 2) {

    // String data = Serial.readStringUntil('\n');
    firstChar = Serial.read();
    secondChar = Serial.read();
    if (firstChar == 'A' && secondChar == 'R') {
      Serial.write("Y\n");
    } else {
      control_main(firstChar, secondChar);
    }
    
    
  }
}
