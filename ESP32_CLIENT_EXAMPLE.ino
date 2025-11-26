
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_PN532.h>

// ==================== CONFIGURATION ====================

// WiFi Credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Edge Service Configuration
const char* EDGE_SERVICE_URL = "http://192.168.1.100:5000"; 
const char* DEVICE_ID = "gym-esp32-001";
const char* API_KEY = "gym-api-key-2025";

// Hardware Pins
#define PN532_SDA 21  // I2C SDA pin
#define PN532_SCL 22  // I2C SCL pin
#define PULSE_SENSOR_PIN 34  // Analog pin for pulse sensor
#define LED_PIN 2  // Built-in LED for visual feedback

// Pulse Sensor Configuration
#define SAMPLES_PER_READING 10
#define READING_INTERVAL 5000  // Send BPM every 5 seconds

// ==================== GLOBAL VARIABLES ====================

Adafruit_PN532 nfc(PN532_SDA, PN532_SCL);

int currentMemberId = 0;
int currentSessionId = 0;
bool isSessionActive = false;
unsigned long lastBPMSend = 0;

// ==================== SETUP ====================

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  
  Serial.println("\n=== PumpUp Gym ESP32 Client ===");
  
  // Initialize WiFi
  connectWiFi();
  
  // Initialize NFC
  initNFC();
  
  Serial.println("System ready!");
  Serial.println("Waiting for NFC card...");
}

// ==================== MAIN LOOP ====================

void loop() {
  // Check for NFC card
  checkNFCCard();
  
  // If session is active, monitor heart rate
  if (isSessionActive) {
    monitorHeartRate();
  }
  
  delay(100);
}

// ==================== WIFI FUNCTIONS ====================

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

// ==================== NFC FUNCTIONS ====================

void initNFC() {
  Serial.println("Initializing PN532...");
  nfc.begin();
  
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("PN532 not found!");
    while (1);  // Stop execution
  }
  
  Serial.print("Found PN532 with firmware version: ");
  Serial.println(versiondata, HEX);
  
  nfc.SAMConfig();
  Serial.println("PN532 ready!");
}

void checkNFCCard() {
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength;
  
  if (nfc.readPassiveTargetID(PN_MIFARE_ISO14443A, uid, &uidLength, 100)) {
    // Convert UID to hex string
    String nfcUID = "";
    for (uint8_t i = 0; i < uidLength; i++) {
      if (uid[i] < 0x10) nfcUID += "0";
      nfcUID += String(uid[i], HEX);
    }
    nfcUID.toUpperCase();
    
    Serial.println("\n=== NFC Card Detected ===");
    Serial.print("UID: ");
    Serial.println(nfcUID);
    
    // Process NFC scan
    processNFCScan(nfcUID);
    
    // Wait for card to be removed
    delay(2000);
    while (nfc.readPassiveTargetID(PN_MIFARE_ISO14443A, uid, &uidLength, 100)) {
      delay(100);
    }
    Serial.println("Card removed\n");
  }
}

// ==================== PULSE SENSOR FUNCTIONS ====================

float readBPM() {
  // Simple BPM reading from analog pulse sensor
  // This is a basic implementation - for production use a proper library
  
  int total = 0;
  for (int i = 0; i < SAMPLES_PER_READING; i++) {
    total += analogRead(PULSE_SENSOR_PIN);
    delay(10);
  }
  
  int average = total / SAMPLES_PER_READING;
  
  // Convert analog reading to approximate BPM (this is simplified)
  // Adjust the formula based on your specific pulse sensor
  float bpm = map(average, 0, 4095, 60, 180);
  
  return bpm;
}

void monitorHeartRate() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastBPMSend >= READING_INTERVAL) {
    float bpm = readBPM();
    
    Serial.print("Heart Rate: ");
    Serial.print(bpm);
    Serial.println(" BPM");
    
    // Send to edge service
    recordHeartRate(bpm);
    
    lastBPMSend = currentTime;
  }
}

// ==================== API FUNCTIONS ====================

void processNFCScan(String nfcUID) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Error: WiFi not connected");
    blinkLED(3);
    return;
  }
  
  HTTPClient http;
  String url = String(EDGE_SERVICE_URL) + "/api/v1/access/nfc-scan";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["nfc_uid"] = nfcUID;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  Serial.println("Sending NFC scan to edge service...");
  int httpCode = http.POST(requestBody);
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.print("Response: ");
    Serial.println(response);
    
    // Parse response
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);
    
    bool success = responseDoc["success"];
    String action = responseDoc["action"].as<String>();
    
    if (success) {
      if (action == "check_in") {
        currentMemberId = responseDoc["member_id"];
        Serial.println("✓ Check-in successful!");
        Serial.print("Member: ");
        Serial.println(responseDoc["member_name"].as<String>());
        blinkLED(2);
        
        // Automatically start equipment session
        delay(1000);
        startEquipmentSession();
        
      } else if (action == "check_out") {
        Serial.println("✓ Check-out successful!");
        blinkLED(2);
        
        // End equipment session if active
        if (isSessionActive) {
          endEquipmentSession();
        }
        
        currentMemberId = 0;
      }
    } else {
      Serial.print("✗ Access denied: ");
      Serial.println(responseDoc["reason"].as<String>());
      blinkLED(5);
    }
  } else {
    Serial.print("Error: HTTP ");
    Serial.println(httpCode);
    blinkLED(3);
  }
  
  http.end();
}

void startEquipmentSession() {
  if (WiFi.status() != WL_CONNECTED || currentMemberId == 0) {
    return;
  }
  
  HTTPClient http;
  String url = String(EDGE_SERVICE_URL) + "/api/v1/equipment/session/start";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);
  
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["member_id"] = currentMemberId;
  doc["equipment_id"] = 1;  // Test equipment ID
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  Serial.println("Starting equipment session...");
  int httpCode = http.POST(requestBody);
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.println(response);
    
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);
    
    if (responseDoc["success"]) {
      currentSessionId = responseDoc["session_id"];
      isSessionActive = true;
      Serial.println("✓ Equipment session started!");
      Serial.print("Session ID: ");
      Serial.println(currentSessionId);
      blinkLED(1);
    }
  }
  
  http.end();
}

void endEquipmentSession() {
  if (WiFi.status() != WL_CONNECTED || !isSessionActive) {
    return;
  }
  
  HTTPClient http;
  String url = String(EDGE_SERVICE_URL) + "/api/v1/equipment/session/end";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);
  
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["member_id"] = currentMemberId;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  Serial.println("Ending equipment session...");
  int httpCode = http.POST(requestBody);
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.println(response);
    
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);
    
    if (responseDoc["success"]) {
      Serial.println("✓ Equipment session ended!");
      isSessionActive = false;
      currentSessionId = 0;
      blinkLED(1);
    }
  }
  
  http.end();
}

void recordHeartRate(float bpm) {
  if (WiFi.status() != WL_CONNECTED || !isSessionActive) {
    return;
  }
  
  HTTPClient http;
  String url = String(EDGE_SERVICE_URL) + "/api/v1/equipment/heart-rate";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);
  
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["session_id"] = currentSessionId;
  doc["member_id"] = currentMemberId;
  doc["bpm"] = bpm;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  int httpCode = http.POST(requestBody);
  
  if (httpCode > 0) {
    String response = http.getString();
    
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);
    
    if (responseDoc["success"]) {
      Serial.println("✓ Heart rate recorded");
    } else {
      Serial.print("✗ Error: ");
      Serial.println(responseDoc["error"].as<String>());
    }
  }
  
  http.end();
}

// ==================== UTILITY FUNCTIONS ====================

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}
