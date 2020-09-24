/*
  WiFi web server to display a red or green tally light.

  based on original sketch by Tom Igoe, created 25 Nov 2012
*/
#include <SPI.h>
#include <WiFiNINA.h>

#include "arduino_secrets.h";
char ssid[] = WLAN_SSID;
char pass[] = WLAN_PASSWORD;

int redPin = 9;
int greenPin = 12;

// polling management
// expect a heartbeat every 4s to prevent interruptions.
// STALE value should be hb interval * 2 to prevent false shutdowns
const unsigned long HEARTBEAT_STALE = 8000;
unsigned long now;
unsigned long last_received_at = 0;

// connection management
int wifi_status = WL_IDLE_STATUS;
WiFiServer server(80);
unsigned long last_wifi_status_check_at = 0;
const unsigned long WIFI_STATUS_CHECK_INTERVAL = 30 * 1000;

// connect wifi and start HTTP server if needed.
// includes polling behavior, so will only re-check every WIFI_STATUS_CHECK_INTERVAL unless forced.
void restartNetworkingIfNeeded(bool forceCheck = false) {
  now = millis();
  if (forceCheck || ((now - last_wifi_status_check_at) >= WIFI_STATUS_CHECK_INTERVAL)) {
    wifi_status = WiFi.status();

    if (wifi_status != WL_CONNECTED) {
      while (wifi_status != WL_CONNECTED) {
        WiFi.begin(ssid, pass);

        // wait 10 seconds for connection:
        // indicate no connection by blinking red LED.
        for(int i = 0; i < 5; i++) {
          digitalWrite(redPin, HIGH);
          delay(50);
          digitalWrite(redPin, LOW);
          delay(1950);
        }

        wifi_status = WiFi.status();
      }

      server.begin();
      Serial.println("started server.");

      // use green pin to indicate wifi is connected.
      digitalWrite(greenPin, HIGH);
      delay(500);
      digitalWrite(greenPin, LOW);
    } else {
      Serial.println("wifi check OK.");
    }

    last_wifi_status_check_at = millis();
  }
}

void setup() {
  IPAddress ip;
  byte mac[6];

  Serial.begin(9600);      // initialize serial communication
  //  while (!Serial) ;

  pinMode(redPin,   OUTPUT);
  pinMode(greenPin, OUTPUT);

  WiFi.macAddress(mac);
  String macAddr = String(mac[5], HEX) +
                   String(":") +
                   String(mac[4], HEX) +
                   String(":") +
                   String(mac[3], HEX) +
                   String(":") +
                   String(mac[2], HEX) +
                   String(":") +
                   String(mac[1], HEX) +
                   String(":") +
                   String(mac[0], HEX);

  // unit A. second one i built. heat shrink all the way up to the end of the LED.
  // with Camera A
  if (macAddr.compareTo(String("30:ae:a4:bc:31:1c")) == 0) {
    ip = IPAddress(10, 4, 2, 12);
  // unit B. first one i built. red wire visible at base of LED.
  // with Camera B.
  } else if (macAddr.compareTo(String("4c:11:ae:d1:13:8")) == 0) {
    ip = IPAddress(10, 4, 2, 13);
  } else {
//    Serial.println("unable to determine IP address.");
  }

  // set static IP address, determined from MAC address above.
  // arduino-based DHCP, lol.
  WiFi.config(ip);

  restartNetworkingIfNeeded(true);

  printWifiStatus();
}

void loop() {
  WiFiClient client = server.available();

  if (client) {
    String currentLine = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n') {
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();

            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            break;
          } else {    // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }

        // TODO: RGB LED with different on/off colors.
        // on, off, no-signal (LED off).
        if (currentLine.endsWith("GET /RED")) {
          digitalWrite(redPin, HIGH);
          digitalWrite(greenPin, LOW);
          last_received_at = millis();
        } else if (currentLine.endsWith("GET /GREEN")) {
          digitalWrite(redPin, LOW);
          digitalWrite(greenPin, HIGH);
          last_received_at = millis();
        }
      }
    }
    // close the connection:
    client.stop();
  }

  // make sure we're still getting heartbeats.
  now = millis();
  if ((now - last_received_at) >= HEARTBEAT_STALE) {
    digitalWrite(redPin, LOW);
    digitalWrite(greenPin, LOW);
  }

  restartNetworkingIfNeeded();
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
  // print where to go in a browser:
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
}
