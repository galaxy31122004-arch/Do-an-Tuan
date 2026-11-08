#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <time.h>
#include "settings.h"
#include "../../common/protocol.h"

struct Sample { measurement_t value; uint32_t arrived; };
static QueueHandle_t samples;
static HardwareSerial hostUart(1); /* ESP32-C3 has UART0/UART1; USB CDC is the console. */
static volatile bool cloudOk=false;
static volatile uint32_t lastSuccess=0;
static volatile uint32_t lastSuccessEpoch=0;
static uint32_t lineErrors=0;

static void sendControl(char kind,const char *body) {
    char payload[64],wire[80];
    snprintf(payload,sizeof payload,"%c,%s",kind,body);
    snprintf(wire,sizeof wire,"$%s*%02X\n",payload,frame_crc(payload));
    hostUart.print(wire);
}

/* Dedicated UART task keeps consuming frames while HTTPS blocks in loop(). */
static void uartTask(void *) {
    char line[96]; size_t used=0; bool dropping=false;
    uint32_t statusAt=0,syncAt=0;
    for(;;) {
        while(hostUart.available()) {
            char c=(char)hostUart.read();
            if(c=='$') { used=0; dropping=false; }
            if(c=='\r') continue;
            if(c=='\n') {
                if(!dropping&&used) {
                    line[used]=0; Sample s;
                    if(parse_measurement(line,&s.value)) {
                        s.arrived=millis();
                        time_t received=time(nullptr);
                        /* Timestamp near frame reception; the AT89S52 only mirrors time for display. */
                        if(received>=1704067200) { s.value.epoch=(uint32_t)received; s.value.flags|=2; }
                        else { s.value.epoch=0; s.value.flags&=(uint8_t)~2; }
                        xQueueOverwrite(samples,&s);
                    }
                    else ++lineErrors;
                }
                used=0; dropping=false;
            } else if(!dropping) {
                if(used<sizeof line-1) line[used++]=c; else dropping=true;
            }
        }
        uint32_t now=millis();
        if(now-statusAt>=1000) {
            char body[48];
            bool freshCloud=cloudOk&&(now-lastSuccess<30000);
            snprintf(body,sizeof body,"%u,%u,%lu",WiFi.status()==WL_CONNECTED,freshCloud,(unsigned long)lastSuccessEpoch);
            sendControl('S',body); statusAt=now;
        }
        time_t utc=time(nullptr);
        if(now-statusAt>200 && now-statusAt<800 && (!syncAt||now-syncAt>=1000)) {
            char body[16]; snprintf(body,sizeof body,"%lu",utc>=1704067200?(unsigned long)utc:0UL);
            sendControl('T',body); syncAt=now?now:1;
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

static bool configured() {
    return String(WIFI_SSID)!="YOUR_WIFI_SSID" && String(IOT_TOKEN)!="YOUR_DEVICE_ACCESS_TOKEN"
        && String(IOT_ORIGIN).startsWith("https://")
        && String(IOT_ROOT_CA).indexOf("REPLACE_WITH")<0;
}

static bool publish(const Sample &s) {
    WiFiClientSecure tls;
    tls.setCACert(IOT_ROOT_CA); tls.setHandshakeTimeout(5);
    HTTPClient http;
    String url=String(IOT_ORIGIN)+"/api/v1/"+IOT_TOKEN+"/telemetry";
    if(!http.begin(tls,url)) return false;
    http.setConnectTimeout(5000); http.setTimeout(5000);
    http.addHeader("Content-Type","application/json");
    char values[320],body[400];
    const measurement_t &m=s.value;
    /* Omit invalid measurements rather than publishing fabricated zero values. */
    if(m.flags&1) {
        snprintf(values,sizeof values,"{\"temperature\":%.1f,\"humidity\":%.1f,\"sensor_ok\":true,\"time_ok\":%s,\"sequence\":%lu,\"rssi\":%d,\"demo\":%s}",
            m.temperature10/10.0,m.humidity10/10.0,(m.flags&2)?"true":"false",(unsigned long)m.sequence,WiFi.RSSI(),DEMO_MODE?"true":"false");
    } else snprintf(values,sizeof values,"{\"sensor_ok\":false,\"time_ok\":%s,\"sequence\":%lu,\"rssi\":%d,\"demo\":%s}",
        (m.flags&2)?"true":"false",(unsigned long)m.sequence,WiFi.RSSI(),DEMO_MODE?"true":"false");
    if(m.flags&2) snprintf(body,sizeof body,"{\"ts\":%llu,\"values\":%s}",(unsigned long long)m.epoch*1000ULL,values);
    else snprintf(body,sizeof body,"%s",values); /* Server timestamps if a valid UTC stamp is unavailable. */
    int code=http.POST((uint8_t*)body,strlen(body));
    http.end();
    Serial.printf("Telemetry HTTP %d; seq=%lu; UART errors=%lu\n",code,(unsigned long)m.sequence,(unsigned long)lineErrors);
    return code>=200&&code<300;
}

void setup() {
    digitalWrite(LEVEL_OE_PIN,LOW);
    pinMode(LEVEL_OE_PIN,OUTPUT);
    Serial.begin(115200);
    samples=xQueueCreate(1,sizeof(Sample));
    if(!samples) { Serial.println("Queue allocation failed"); abort(); }
    hostUart.setRxBufferSize(256); hostUart.begin(9600,SERIAL_8N1,AT89S52_RX_PIN,AT89S52_TX_PIN);
    delay(100); /* VCCA/VCCB settle; R4 holds OE low before GPIO configuration. */
    digitalWrite(LEVEL_OE_PIN,HIGH);
    WiFi.mode(WIFI_STA); WiFi.setAutoReconnect(true);
    if(configured()) WiFi.begin(WIFI_SSID,WIFI_PASSWORD);
    else Serial.println("Configure include/secrets.h with Wi-Fi, HTTPS host, device token and CA.");
    configTime(0,0,"pool.ntp.org","time.google.com");
    xTaskCreate(uartTask,"host-uart",4096,nullptr,1,nullptr);
    Serial.println(DEMO_MODE?"DEMO: synthetic data, not sensor readings":"LIVE: waiting for AT89S52 frames");
}

void loop() {
    static uint32_t attempt=0,wifiAttempt=0,demoAt=0,sequence=0;
    static bool wasConnected=false;
    uint32_t now=millis(); bool connected=WiFi.status()==WL_CONNECTED;
    if(!connected) {
        cloudOk=false;
        if(configured()&&now-wifiAttempt>=WIFI_RETRY_MS) { WiFi.reconnect(); wifiAttempt=now; }
    }
    if(connected&&!wasConnected) {
        xQueueReset(samples); /* Discard the last offline sample. Await a new measurement. */
        attempt=now-SEND_INTERVAL_MS;
    }
    wasConnected=connected;
    if(DEMO_MODE&&now-demoAt>=2000) {
        Sample s={}; s.value.sequence=++sequence; s.value.epoch=(uint32_t)time(nullptr);
        s.value.temperature10=250+(int16_t)(sequence%20); s.value.humidity10=600+(sequence%30);
        s.value.flags=time(nullptr)>=1704067200?3:1; s.arrived=now;
        xQueueOverwrite(samples,&s); demoAt=now;
    }
    if(connected&&configured()&&time(nullptr)>=1704067200&&now-attempt>=SEND_INTERVAL_MS) {
        Sample s;
        if(xQueueReceive(samples,&s,0)==pdTRUE&&now-s.arrived<=STALE_MS) {
            attempt=now; cloudOk=publish(s);
            if(cloudOk) { lastSuccess=millis(); lastSuccessEpoch=(uint32_t)time(nullptr); }
            /* No retry queue: failed/offline historical records are intentionally dropped. */
        }
    }
    delay(10);
}
