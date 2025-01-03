#include <Servo.h>

#define MIN_SPEED 0
#define MAX_SPEED 255
#define SLOW 50
#define MEDIUM 150
#define FAST 200
#define DEFAULT_DELAY_MS 200

#define SERVO_OPEN  (50)
#define SERVO_CLOSE  (125)

#define IN1  7
#define IN2 6
#define IN3 5
#define IN4 4

Servo myservo;
volatile char firstChar, secondChar;
volatile bool check = false;
volatile bool servo_is_open = false;

void halt() {
//  PORTD &= ~((1 << IN1) | (1 << IN4) | (1 << IN2) | (1 << IN3));
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void forward(int speed) {
  halt();
  PORTD |= ((1 << IN1) | (1 << IN4));
  analogWrite(IN3, 255 - speed);
  analogWrite(IN2, 255 - speed);

  
//  digitalWrite(IN1, HIGH);
//  digitalWrite(IN4, HIGH);
  
}

void reverse(int speed) {
//  digitalWrite(IN1, LOW);
//  digitalWrite(IN4, LOW);
  PORTD &= ~((1 << IN1) | (1 << IN4));
  
  analogWrite(IN2, speed);
  analogWrite(IN3, speed);
}

void left(int speed) {
  digitalWrite(IN1, HIGH);
  
  digitalWrite(IN4, LOW);
  analogWrite(IN2, speed);
  analogWrite(IN3, speed);
}

void steer_left(int speed) {
  halt();
//  PORTD |= ((1 << IN1) | (1 << IN4));
//  analogWrite(IN3, 255 - speed*4/1.5);
////  digitalWrite(/IN1, HIGH);
//  analogWrite(IN2, 255 - speed);
  digitalWrite(IN1, HIGH);
  analogWrite(IN2, speed);
}

void right(int speed) {
  digitalWrite(IN1, LOW);
  
  digitalWrite(IN4, HIGH);
  analogWrite(IN2, speed);
  analogWrite(IN3, speed);
}

void steer_right(int speed) {
  halt();
//  PORTD |= ((1 << IN1) | (1 << IN4));/
  digitalWrite(IN4, HIGH);
  analogWrite(IN3, speed);
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
  } else if (c1 == 'l') {
    steer_left(speed);
  } else if (c1 == 'r') {
    steer_right(speed);
  } else if (c1 == 'O') {
    if (servo_is_open) {
      
    } else {
      for (int i = SERVO_CLOSE; i >= SERVO_OPEN; i--) {
        myservo.write(i);
        delay(10);
      }
      servo_is_open = true;
    }
  } else if (c1 == 'C') {
    if (servo_is_open) {
      for (int i = SERVO_OPEN; i <= SERVO_CLOSE; i++) {
        myservo.write(i);
        delay(10);
      }
      servo_is_open = false;
    } else {
      
    }
  } else {
    // Pass
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
//  pinMod/e(CHECK, INPUT);
  myservo.attach(3); 
  myservo.write(SERVO_CLOSE);
  halt();
}

void loop() {
  // forward(MEDIUM);
  if (Serial.available() >= 2) {

    // String data = Serial.readStringUntil('\n');
    firstChar = Serial.read();
    secondChar = Serial.read();
    if (!check) {
      if (firstChar == 'A' && secondChar == 'R') {
        Serial.write("Y\n");
        check = true;
      }
    } else {
      control_main(firstChar, secondChar);
    }   
    
  }
}
