    #include <WiFi.h>
    #include <HTTPClient.h>
    #include <Wire.h>
    #include <SPI.h>
    #include <PN532_SPI.h>
    #include "PN532.h"
    #include <MAX30105.h>
    #include "heartRate.h"
    #include <ArduinoJson.h>

    // ==================== CONFIGURACION BASICA ====================

    // WiFi (usa tu SSID/clave reales de 2.4 GHz)
    const char* WIFI_SSID = "iPhone de Mateo";
    const char* WIFI_PASSWORD = "12345678";

    // Edge API (Flask app.py) - apunta a la laptop que corre el servicio
    const char* EDGE_API_BASE_URL = "http://172.20.10.3:5000";
    const char* DEVICE_ID = "gym-esp32-001";
    const char* API_KEY = "gym-api-key-2025";

    // Pines PN532 en modo SPI (segun tu conexion actual)
    #define PN532_SCK 18
    #define PN532_MOSI 23
    #define PN532_MISO 19
    #define PN532_SS 5

    // Pines MAX30102 (I2C) segun tu conexion actual
    #define I2C_SDA 21
    #define I2C_SCL 22

    // Sensor ritmo cardiaco
    const long FINGER_THRESHOLD = 71074;     // Umbral para detectar dedo
    const unsigned long BPM_SEND_INTERVAL = 5000; // Enviar BPM cada 5s

    // Feedback (no LED available, so LED logic is disabled)
    #define LED_PIN -1

    // ==================== ESTADO ====================

    PN532_SPI pn532spi(SPI, PN532_SS);
    PN532 nfc(pn532spi);
    MAX30105 heartSensor;

    String activeMemberId = "";      // ID de miembro devuelto por el edge al hacer check-in
    unsigned long lastBeatTime = 0;  // Para calcular BPM
    unsigned long lastSendTime = 0;
    float lastValidBPM = 0;

    // ==================== SETUP ====================

    void setup() {
      Serial.begin(115200);
      // No LED available; skip pin setup.
      Wire.begin(I2C_SDA, I2C_SCL);

      Serial.println("\n=== Edge - NFC + Ritmo Cardiaco ===");

      connectWiFi();
      initNFC();
      initHeartSensor();

      Serial.println("Listo. Acerque tarjeta y coloque dedo en el sensor.");
    }

    // ==================== LOOP ====================

    void loop() {
      readNFCTag();
      monitorHeartRate();
      delay(20);
    }

    // ==================== WIFI ====================

    void connectWiFi() {
      Serial.print("Conectando a WiFi");
      WiFi.mode(WIFI_STA);
      WiFi.setSleep(false);
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

      int attempts = 0;
      const int MAX_ATTEMPTS = 60; // 60 intentos * 500ms = 30s
      while (WiFi.status() != WL_CONNECTED && attempts < MAX_ATTEMPTS) {
        delay(500);
        Serial.print(".");
        attempts++;
      }

      if (WiFi.status() == WL_CONNECTED) {
        Serial.print("\nWiFi OK. IP: ");
        Serial.println(WiFi.localIP());
      } else {
        Serial.println("\nNo se pudo conectar a WiFi.");
      }
    }

    bool ensureWiFi() {
      if (WiFi.status() == WL_CONNECTED) return true;
      connectWiFi();
      return WiFi.status() == WL_CONNECTED;
    }

    // ==================== NFC (PN532 SPI) ====================

    void initNFC() {
      Serial.println("Inicializando PN532 (SPI)...");
      nfc.begin();

      uint32_t versiondata = nfc.getFirmwareVersion();
      if (!versiondata) {
        Serial.println("No se detecto PN532. Revisa cableado/modo SPI.");
        while (1) { delay(100); }
      }

      Serial.print("PN532 detectado. FW: ");
      Serial.println(versiondata, HEX);
      nfc.SAMConfig();
      Serial.println("NFC listo.");
    }

    void readNFCTag() {
      uint8_t uid[7];
      uint8_t uidLength;

      if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength)) {
        String uidHex = "";
        for (uint8_t i = 0; i < uidLength; i++) {
          if (uid[i] < 0x10) uidHex += "0";
          uidHex += String(uid[i], HEX);
        }
        uidHex.toUpperCase();

        Serial.print("\nTarjeta detectada. UID: ");
        Serial.println(uidHex);

        sendNfcScan(uidHex);

        // Esperar a que se retire la tarjeta
        delay(1000);
        while (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength)) {
          delay(50);
        }
        Serial.println("Tarjeta retirada.\n");
      }
    }

    // ==================== MAX30102 ====================

    void initHeartSensor() {
      Serial.println("Inicializando MAX30102...");
      if (!heartSensor.begin(Wire, I2C_SPEED_FAST)) {
        Serial.println("No se encontro MAX30102. Verifica cableado.");
        while (1) { delay(100); }
      }

      heartSensor.setup(
        0x1F,   // Brightness
        4,      // Sample average
        2,      // Mode = Red + IR
        100,    // Sample rate
        411,    // Pulse width
        4096    // ADC range
      );

      heartSensor.setPulseAmplitudeRed(0x1F);
      heartSensor.setPulseAmplitudeIR(0x1F);
      Serial.println("MAX30102 listo.");
    }

    void monitorHeartRate() {
      if (activeMemberId.length() == 0) {
        return;  // Esperar a que alguien se identifique por NFC
      }

      unsigned long now = millis();
      long irValue = heartSensor.getIR();

      if (irValue < FINGER_THRESHOLD) {
        // No enviar nada hasta que haya dedo y BPM valido
        return;
      }

      if (checkForBeat(irValue)) {
        unsigned long delta = now - lastBeatTime;
        lastBeatTime = now;

        float bpm = 60.0 / (delta / 1000.0);
        if (bpm > 40 && bpm < 180) {
          lastValidBPM = bpm;
        }
      }

      if (lastValidBPM > 0 && (now - lastSendTime) >= BPM_SEND_INTERVAL) {
        sendHeartRate(lastValidBPM);
        lastSendTime = now;
      }
    }

    // ==================== API CALLS ====================

    void sendNfcScan(const String& uidHex) {
      if (!ensureWiFi()) return;

      HTTPClient http;
      String url = String(EDGE_API_BASE_URL) + "/api/v1/access/nfc-scan";

      Serial.print("Enviando NFC -> ");
      Serial.println(url);

      http.setConnectTimeout(5000);
      http.begin(url);
      http.addHeader("Content-Type", "application/json");
      http.addHeader("X-API-Key", API_KEY);

      String body = "{\"device_id\":\"" + String(DEVICE_ID) + "\",\"nfc_uid\":\"" + uidHex + "\"}";
      int httpCode = http.POST(body);
      String resp = http.getString();

      Serial.print("HTTP ");
      Serial.print(httpCode);
      Serial.print(" Respuesta: ");
      Serial.println(resp);

      if (httpCode > 0) {
        DynamicJsonDocument doc(512);
        DeserializationError err = deserializeJson(doc, resp);
        if (err) {
          Serial.print("No pude parsear la respuesta JSON: ");
          Serial.println(err.c_str());
          http.end();
          return;
        }

        String action = doc["action"] | "";
        int memberId = doc["member_id"] | 0;

        if (action == "check_in") {
          activeMemberId = memberId > 0 ? String(memberId) : uidHex;
          lastValidBPM = 0;
          lastSendTime = 0;
          Serial.print("Check-in OK. Miembro activo: ");
          Serial.println(activeMemberId);
        } else if (action == "check_out") {
          activeMemberId = "";
          lastValidBPM = 0;
          Serial.println("Check-out OK. Se detiene el envio de BPM.");
        } else {
          Serial.println("Acceso denegado o accion desconocida.");
        }
      }

      http.end();
    }

    void sendHeartRate(float bpm) {
      if (!ensureWiFi()) return;
      if (activeMemberId.length() == 0) return;

      String url = String(EDGE_API_BASE_URL) + "/api/heart-rate/" + activeMemberId;
      HTTPClient http;

      http.setConnectTimeout(5000);
      http.begin(url);
      http.addHeader("Content-Type", "application/json");
      http.addHeader("X-API-Key", API_KEY);

      String body = "{\"bpm\":" + String(bpm, 1) + "}";

      Serial.print("Enviando BPM ");
      Serial.print(bpm);
      Serial.print(" -> ");
      Serial.println(url);

      int httpCode = http.POST(body);
      String resp = http.getString();

      Serial.print("HTTP ");
      Serial.print(httpCode);
      Serial.print(" Respuesta: ");
      Serial.println(resp);

      if (httpCode > 0) {
        // feedback could be added here (e.g., buzzer)
      }

      http.end();
    }
