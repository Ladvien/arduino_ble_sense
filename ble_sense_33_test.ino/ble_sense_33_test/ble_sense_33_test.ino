// https://rootsaid.com/arduino-ble-example/
#include <ArduinoBLE.h>
#include <PDM.h>

// This device's MAC:
// C8:5C:A2:2B:61:86
//#define LEDR        (23u)
//#define LEDG        (22u)
//#define LEDB        (24u)

// BLE Service
BLEService microphoneService("1101");

// Characteristic info.
// https://www.arduino.cc/en/Reference/ArduinoBLEBLECharacteristicBLECharacteristic
BLEByteCharacteristic microphoneLevelCharRead("1142", BLEWrite);
BLEByteCharacteristic microphoneLevelCharWrite("1143", BLERead | BLENotify | BLEBroadcast);

// Buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// Number of samples read
volatile int samplesRead;

/*
 *  Main
 */
void setup() {

  // Start serial.
  Serial.begin(9600);

  // Ensure serial port is ready.
  while (!Serial);

  // Prepare LED pins.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);

  // Configure the data receive callback
  PDM.onReceive(onPDMdata);

  // Start PDM
  startPDM();

  // Start BLE.
  startBLE();

  // Create BLE service and characteristics.
  BLE.setLocalName("MicrophoneMonitor");
  BLE.setAdvertisedService(microphoneService);
  microphoneService.addCharacteristic(microphoneLevelCharRead);
  microphoneService.addCharacteristic(microphoneLevelCharWrite);
  BLE.addService(microphoneService);

  microphoneLevelCharRead.setEventHandler(BLERead, onMicrophoneLevelCharRead);

  // Let's tell devices about us.
  BLE.advertise();
  Serial.println("Bluetooth device active, waiting for connections...");
}


void loop()
{
  BLEDevice central = BLE.central();

  if (central)
  {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    // Only send data if we are connected to a central device.
    while (central.connected()) {
      connectedLight();

      // Send read request.
      byte values[256];
      int numBytes = microphoneLevelCharRead.readValue(values, 256);
      if(numBytes > 0) {
        Serial.print("Got #: ");
        Serial.print(numBytes);
        Serial.println(" of bytes");
        for (int i = 0; i < numBytes; i++) {
          Serial.print(values[i]);
        }
      }
      
//      Serial.println(microphoneLevelCharRead.value());

      // Send the microphone values to the central device.
      if (samplesRead) {
        // print samples to the serial monitor or plotter
        for (int i = 0; i < samplesRead; i++) {
          microphoneLevelCharWrite.writeValue(sampleBuffer[i]);      
        }
        // Clear the read count
        samplesRead = 0;
      }
    }
  } else {
    disconnectedLight();
  }
}


/*
 * Bluetooth
 */
void startBLE() {
  if (!BLE.begin())
  {
    Serial.println("starting BLE failed!");
    while (1);
    disconnectedLight();
  }
}

void onMicrophoneLevelCharRead(BLEDevice central, BLECharacteristic characteristic) {
  // central wrote new value to characteristic, update LED
  Serial.print("Characteristic event, read: ");
  Serial.println(characteristic.value);
}


/*
 * Microphone
 */
void startPDM() {
  // initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate
  if (!PDM.begin(1, 16000)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }
}


void onPDMdata() {
  // query the number of bytes available
  int bytesAvailable = PDM.available();

  // read into the sample buffer
  PDM.read(sampleBuffer, bytesAvailable);

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}


/*
 * LEDS
 */
void connectedLight() {
  digitalWrite(LEDR, LOW);
  digitalWrite(LEDG, HIGH);
}


void disconnectedLight() {
  digitalWrite(LEDR, HIGH);
  digitalWrite(LEDG, LOW);
}
