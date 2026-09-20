/*
 * ==============================================================================
 * CYBERDECK OS - ESP32 Companion Microcontroller Firmware
 * Protocol: JSON over USB Serial (115200 baud)
 * ==============================================================================
 */

#include <Arduino.h>
#include <ArduinoJson.h>

#define LED_PIN 2
#define ADC_PIN 34
#define BAUD_RATE 115200

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  analogReadResolution(12);
}

void processCommand(const String& input) {
  StaticJsonDocument<256> docIn;
  DeserializationError error = deserializeJson(docIn, input);

  if (error) {
    StaticJsonDocument<128> errDoc;
    errDoc["success"] = false;
    errDoc["error"] = "Invalid JSON";
    serializeJson(errDoc, Serial);
    Serial.println();
    return;
  }

  const char* cmd = docIn["command"] | "";
  StaticJsonDocument<256> docOut;

  if (strcmp(cmd, "ping") == 0) {
    docOut["success"] = true;
    docOut["pong"] = true;
    docOut["firmware"] = "CyberDeck-ESP32-v0.1.0";
    docOut["uptime_ms"] = millis();
  }
  else if (strcmp(cmd, "gpio") == 0) {
    int pin = docIn["pin"] | 2;
    bool state = docIn["state"] | false;
    pinMode(pin, OUTPUT);
    digitalWrite(pin, state ? HIGH : LOW);
    docOut["success"] = true;
    docOut["pin"] = pin;
    docOut["state"] = state;
  }
  else if (strcmp(cmd, "read_analog") == 0) {
    int pin = docIn["pin"] | ADC_PIN;
    int raw = analogRead(pin);
    float voltage = (raw / 4095.0) * 3.3;
    docOut["success"] = true;
    docOut["pin"] = pin;
    docOut["raw"] = raw;
    docOut["voltage"] = voltage;
  }
  else if (strcmp(cmd, "telemetry") == 0) {
    int raw = analogRead(ADC_PIN);
    float battery_v = (raw / 4095.0) * 3.3 * 2.0; // Voltage divider 1:2
    docOut["success"] = true;
    docOut["battery_v"] = battery_v;
    docOut["uptime_s"] = millis() / 1000;
  }
  else {
    docOut["success"] = false;
    docOut["error"] = "Unknown command";
  }

  serializeJson(docOut, Serial);
  Serial.println();
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      processCommand(input);
    }
  }
}
