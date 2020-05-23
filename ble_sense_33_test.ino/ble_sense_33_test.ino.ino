// https://rootsaid.com/arduino-ble-example/
#include <ArduinoBLE.h>
#include <PDM.h>

// This device's MAC:
// C8:5C:A2:2B:61:86

// Create BLE Service.
BLEService batteryService("1101");
BLEByteCharacteristic batteryLevelChar("19B10012-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify | BLEBroadcast);

/* Microphone
 *  
 */
// buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// number of samples read
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

  // Start BLE.
  startBLE();
  
  BLE.setLocalName("BatteryMonitor");
  BLE.setAdvertisedService(batteryService);
  batteryService.addCharacteristic(batteryLevelChar);
  BLE.addService(batteryService);

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
    while (central.connected()) {
      connectedLight();
      int battery = analogRead(A0);
      int batteryLevel = map(battery, 0, 1023, 0, 100);
//      Serial.print("Battery: ");
//      Serial.println(batteryLevel);
      batteryLevelChar.writeValue(batteryLevel);
//      delay(200);

    }
  } else {
    disconnectedLight();
    Serial.print("Disconnected from central: ");
    Serial.println(central.address()); 
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
