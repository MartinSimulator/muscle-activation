#include <Arduino.h>

// #define is a preprocessor directive so essentially when the code is compiled, every occurence of ADC_PIN gets replaced with 34
// GPIO34 is the chosen analog pin we're using
#define ADC_PIN          34 // tells the program which pin to read from 

// how many ADC readings we want per second
// we choose 1000 since EMG signals have useful content up to 450 HZ and Hyquist theorem says we sample at at least twice the highest frequencey we care about
#define SAMPLE_RATE_HZ   1000

// time gap between samples in microseconds
// we use microseconds since we use micros() giving us really fine timing control
#define SAMPLE_INTERVAL_US (1000000 / SAMPLE_RATE_HZ)

// stores the timestamp of the last ADC read in microseconds
// uint_32 is an unsigned 32-bit integer, volatiles tells the compiler that this variable can change unexpectedly so never cache it in a register
volatile uint32_t lastSampleTime = 0;


// setup is an Arduino function that runs once when the board powers on/resets
// put initialization code here (pin config, start serial communication, start timers)
void setup() {

  // starts the UART serial communication at 115200 bits per second. This channel lets the esp32 send data to the laptop over USB
  Serial.begin(115200);
  
  // sets how many bits of precision the ADC uses. 12 bits means the ADC outputs values from 0 to 4096. esp32 ADC natively supports 12 bits
  analogReadResolution(12);

  // captures the current time in microseconds at boot
  // micros() is a built-in Arduino function that counts microseconds since the board started
  lastSampleTime = micros();
}


// After setup() finishes, Arduino framework calls loop() in an infinite cycle
void loop() {

  // read current timestamp in microseconds into local var called now (only exists inside function it's declared in)
  uint32_t now = micros();

  // now-lastSampleTime finds how many microseconds have passed since last sample. If the gap is less than SAMPLE_INTERVAL_US, we skip everything and loop again
  if ((now - lastSampleTime) >= SAMPLE_INTERVAL_US) {

    // recond when the sample was taken
    lastSampleTime = now;

    // read the voltage on GPIO34 and convert to a number 0 (0v) to 4096 (3.3V)
    // The Myo9ware outputs a voltage proportional to muscle activation 
    int rawValue = analogRead(ADC_PIN);

    // send the current timestamp over USB serial to laptop and output a value 
    Serial.print(now);
    Serial.print(",");

    // send the ADC reading and then newline character 
    // Python reads one line at a time, so each newline marks the end of one complete sample
    Serial.println(rawValue);
  }
}