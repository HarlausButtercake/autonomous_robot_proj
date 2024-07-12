// Define the pins for PWM output and direction control
// Định nghĩa chân của motor
#define IN1 7  //dir
#define IN2 6  //pwm 
#define IN3 5  //pwm
#define IN4 4  //dir

void setup(){
  Serial.begin(9600);
  // Khởi tạo các chân điều khiển motor là đầu ra
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}
void loop() {
  // Read data from serial port
  if (Serial.available() >= 4) { // Check if there are enough bytes available
    // Read PWM values
    int pwmValue1 = Serial.parseInt();
    Serial.println(pwmValue1);
    int pwmValue2 = Serial.parseInt();
    Serial.println(pwmValue2);
    // Read direction values
    //int dirValue1 = Serial.parseInt();
    //Serial.println(dirValue1);
    //int dirValue2 = Serial.parseInt();
    //Serial.println(dirValue2);
    // Set direction pins based on received values
    digitalWrite(IN1, LOW);
    analogWrite(IN2, pwmValue1);
    analogWrite(IN3, pwmValue2);
    digitalWrite(IN4, HIGH);
    delay(500);
  }
}
