#define TOF_TO_DIST(TOF)          ((TOF * 340000) /2 / 1000000 /10)
//#define TOF_TO_DIST(TOF)          ((TOF/2) / 29.1)
#define DIST_TO_TOF(DIST)         ((DIST) * 2000000 / 340000)
#define TOF_IGNORE                (6000)          // Approx. 1 meter
#define DELAY                     (25)

#define ECHO1                     (4)
#define ECHO2                     (5)
#define ECHO3                     (6)
#define ECHO4                     (7)

#define TRIG1                     (8)
#define TRIG2                     (9)
#define TRIG3                     (10)
#define TRIG4                     (11)


volatile unsigned long time_micros[4];
volatile unsigned long time_loop = 0;
volatile char character[2];
volatile bool breakflag = false;

//volatile bool status1 = false;
//volatile bool status2 = false;
//
//volatile bool go1 = false;
//volatile bool go2 = false;
 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(ECHO1, INPUT_PULLUP);
  pinMode(ECHO2, INPUT_PULLUP);
  pinMode(ECHO3, INPUT_PULLUP);
  pinMode(ECHO4, INPUT_PULLUP);
  pinMode(TRIG1, OUTPUT);
  pinMode(TRIG2, OUTPUT);
  pinMode(TRIG3, OUTPUT);
  pinMode(TRIG4, OUTPUT);
//  attachInterrupt(0, ISR1, CHANGE);
//  attachInterrupt(1, ISR2, CHANGE);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  delay(1000);
}

void loop() {
//  go1 = false;
//  Generate 10us pulse
  while (!breakflag) {
    if (Serial.available() >= 2) {
      character[0] = Serial.read();
      character[1] = Serial.read();
      if (character[0] == 'A' && character[1] == 'U') {
        Serial.write("Y\n");
        breakflag = true;
        break;
      } 
    }
  }
  
  time_loop = millis();
  digitalWrite(TRIG1, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG1, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG1, LOW);
  time_micros[0] = pulseIn(ECHO1, HIGH);
  while (millis() - time_loop < DELAY) {
    
  }

  time_loop = millis();
  digitalWrite(TRIG2, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG2, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG2, LOW);
  time_micros[1] = pulseIn(ECHO2, HIGH, TOF_IGNORE);
  while (millis() - time_loop < DELAY) {
    
  }

  time_loop = millis();
  digitalWrite(TRIG3, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG3, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG3, LOW);
  time_micros[2] = pulseIn(ECHO3, HIGH, TOF_IGNORE);
  while (millis() - time_loop < DELAY) {
    
  }

  time_loop = millis();
  digitalWrite(TRIG4, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG4, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG4, LOW);
  time_micros[3] = pulseIn(ECHO4, HIGH, TOF_IGNORE);
  while (millis() - time_loop < DELAY) {
    
  }
  
  Serial.print(TOF_TO_DIST(time_micros[0]));
  Serial.print(" ");
  Serial.print(TOF_TO_DIST(time_micros[1]));
  Serial.print(" ");
  Serial.print(TOF_TO_DIST(time_micros[2]));
  Serial.print(" ");
  Serial.print(TOF_TO_DIST(time_micros[3]));
  Serial.println("");
}

//unsigned long pulseIn(uint8_t pin, uint8_t state, unsigned long timeout)
//{
//  // cache the port and bit of the pin in order to speed up the
//  // pulse width measuring loop and achieve finer resolution.  calling
//  // digitalRead() instead yields much coarser resolution.
//  uint8_t bit = digitalPinToBitMask(pin);
//  uint8_t port = digitalPinToPort(pin);
//  uint8_t stateMask = (state ? bit : 0);
//  unsigned long width = 0; // keep initialization out of time critical area
//  
//  // convert the timeout from microseconds to a number of times through
//  // the initial loop; it takes 16 clock cycles per iteration.
//  unsigned long numloops = 0;
//  unsigned long maxloops = microsecondsToClockCycles(timeout) / 16;
//  
//  // wait for any previous pulse to end
//  while ((*portInputRegister(port) & bit) == stateMask)
//    if (numloops++ == maxloops)
//      return 0;
//  
//  // wait for the pulse to start
//  while ((*portInputRegister(port) & bit) != stateMask)
//    if (numloops++ == maxloops)
//      return 0;
//  
//  // wait for the pulse to stop
//  while ((*portInputRegister(port) & bit) == stateMask) {
//    if (numloops++ == maxloops)
//      return 0;
//    width++;
//  }
//
//  // convert the reading to microseconds. The loop has been determined
//  // to be 20 clock cycles long and have about 16 clocks between the edge
//  // and the start of the loop. There will be some error introduced by
//  // the interrupt handlers.
//  return clockCyclesToMicroseconds(width * 21 + 16); 
//}

//void ISR1() {
//  if ((PIND >> 2) & 0b1 == 1) {
//    status1 = false;
//    time1 = micros();
//  } else {
//    time1 = micros() - time1;
//    status1 = true;
//  }
//}

//void ISR2() {
//  if ((PIND >> 3) & 0b1 == 0b1) {
//    status2 = false;
//    time2 = micros();
//  } else {
//    time2 = micros() - time2;
//    status2 = true;
//  }
//}
