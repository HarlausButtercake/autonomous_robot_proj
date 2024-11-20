#define TOF_TO_DIST(TOF)          ((TOF * 340000) /2 / 1000000 /10)
//#define TOF_TO_DIST(TOF)          ((TOF/2) / 29.1)
#define DIST_TO_TOF(DIST)         ((DIST) * 2000000 / 340000)
#define TOF_IGNORE                (6000)          // Approx. 1 meter
#define DELAY                     (50000)


volatile unsigned long time_micros[4];
volatile unsigned long time_loop = 0;
volatile unsigned long big_loop = 0;

//volatile bool status1 = false;
//volatile bool status2 = false;
//
//volatile bool go1 = false;
//volatile bool go2 = false;
 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
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
  time_loop = micros();
//  big_loop = time_loop;
  digitalWrite(6, LOW);
  delayMicroseconds(2);
  digitalWrite(6, HIGH);
  delayMicroseconds(10);
  digitalWrite(6, LOW);
  time_micros[0] = pulseIn(2, HIGH);
  Serial.println(time_micros[0]);
  while (micros() - time_loop < DELAY) {
    
  }

//  time_loop = micros();
//  digitalWrite(7, LOW);
//  delayMicroseconds(2);
//  digitalWrite(7, HIGH);
//  delayMicroseconds(10);
//  digitalWrite(7, LOW);
//  time_micros[1] = pulseIn(3, HIGH, TOF_IGNORE);
//  while (micros() - time_loop < DELAY) {
//    
//  }
//
//  time_loop = micros();
//  digitalWrite(8, LOW);
//  delayMicroseconds(2);
//  digitalWrite(8, HIGH);
//  delayMicroseconds(10);
//  digitalWrite(8, LOW);
//  time_micros[2] = pulseIn(4, HIGH, TOF_IGNORE);
//  while (micros() - time_loop < DELAY) {
//    
//  }
//  
//  Serial.print(TOF_TO_DIST(time_micros[0]));
//  Serial.print(" ");
//  Serial.print(TOF_TO_DIST(time_micros[1]));
//  Serial.print(" ");
//  Serial.print(TOF_TO_DIST(time_micros[2]));
//  Serial.println("");
//  while (micros() - time_loop < 30000 && time_micros[2] != 0) {
//    
//  }
//  delay(50);
//  go1 = true;
//  delay(50);
////  time1 = pulseIn();
//  if (status1) {
//    Serial.println(TOF_TO_DIST(time1));
//    Serial.print(" ");
//  }
//  if (status2) {
//    Serial.println(TOF_TO_DIST(time2));
//  } else {
//    Serial.println("");
//  }
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
