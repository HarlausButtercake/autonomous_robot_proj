#define TOF_TO_DIST(TOF)          ((TOF * 340000) /2 / 1000000)


volatile unsigned long time1 = 0;
volatile unsigned long time2 = 0;

volatile bool status1 = false;
volatile bool status2 = false;
 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  attachInterrupt(0, ISR1, CHANGE);
  attachInterrupt(1, ISR2, CHANGE);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  delay(1000);
}

void loop() {
  PORTD |= (3 << 6);
  delayMicroseconds(10);
  PORTD &= ~(3 << 6);
  delay(50);
  if (status1) {
    Serial.print(TOF_TO_DIST(time1));
    Serial.print(" ");
  }
  if (status2) {
    Serial.println(TOF_TO_DIST(time2));
  } else {
    Serial.println("");
  }
}

void ISR1() {
  if ((PIND >> 2) & 0b1 == 1) {
    status1 = false;
    time1 = micros();
  } else {
    time1 = micros() - time1;
    status1 = true;
  }
}

void ISR2() {
  if ((PIND >> 3) & 0b1 == 1) {
    status2 = false;
    time2 = micros();
  } else {
    time2 = micros() - time2;
    status2 = true;
  }
}
