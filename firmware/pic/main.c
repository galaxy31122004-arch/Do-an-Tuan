/* Target: PIC16F877A, MPLAB XC8 v2/v3, external 20 MHz crystal. */
#include <xc.h>
#include <stdint.h>
#include <stdbool.h>
#include "board.h"
#include "../common/protocol.h"
#include "../common/clock.h"
#pragma config FOSC=HS, WDTE=OFF, PWRTE=ON, BOREN=ON, LVP=OFF, CPD=OFF, WRT=OFF, CP=OFF

/* RX lives in interrupt context; each incoming line fits in 48 bytes. */
static volatile char rx[48];
static volatile uint8_t rx_used=0,rx_ready=0;
static uint8_t wifi_ok=0,cloud_ok=0;
static uint32_t last_send_uptime=0;
static uint16_t status_age=600;
static uint8_t tx_crc;
static bool oled_ready=false;
static utc_mirror_t clock_mirror={0};

void __interrupt() irq(void) {
    if(PIR1bits.RCIF) {
        char c;
        if(RCSTAbits.OERR) { RCSTAbits.CREN=0; RCSTAbits.CREN=1; }
        if(RCSTAbits.FERR) { c=RCREG; (void)c; return; }
        c=RCREG;
        if(rx_ready) return;
        if(c=='$') rx_used=0;
        if(c=='\r') return;
        if(c=='\n') { rx[rx_used]=0; rx_ready=1; }
        else if(rx_used<sizeof(rx)-1) rx[rx_used++]=c;
        else rx_used=0;
    }
}
static void uart_raw(char c) { while(!PIR1bits.TXIF) {} TXREG=c; }
static void uart_body(char c) { tx_crc=crc8_update(tx_crc,(uint8_t)c); uart_raw(c); }
static void uart_num(uint32_t n) {
    uint32_t divisor=1000000000UL;
    while(divisor>1&&n<divisor) divisor/=10;
    do { uart_body((char)('0'+n/divisor)); n%=divisor; divisor/=10; } while(divisor);
}
static void measurement(uint32_t seq,uint32_t epoch,uint16_t temp,uint16_t humidity,uint8_t flags) {
    static const char hex[]="0123456789ABCDEF";
    uart_raw('$'); tx_crc=0; uart_body('M'); uart_body(','); uart_num(seq);
    uart_body(','); uart_num(epoch); uart_body(','); uart_num(temp);
    uart_body(','); uart_num(humidity); uart_body(','); uart_num(flags);
    uart_raw('*'); uart_raw(hex[tx_crc>>4]); uart_raw(hex[tx_crc&15]); uart_raw('\n');
}
static bool i2c_idle(void) {
    uint16_t guard=60000;
    while((SSPCON2&0x1F)||(SSPSTAT&0x04)) if(!--guard) { SSPCONbits.SSPEN=0; SSPCONbits.SSPEN=1; return false; }
    return true;
}
static bool i2c_start(void) { if(!i2c_idle()) return false; SSPCON2bits.SEN=1; return i2c_idle(); }
static void i2c_stop(void) { if(i2c_idle()) { SSPCON2bits.PEN=1; (void)i2c_idle(); } }
static bool i2c_write(uint8_t data) {
    uint16_t guard=60000;
    if(!i2c_idle()) return false;
    PIR1bits.SSPIF=0; SSPBUF=data;
    while(!PIR1bits.SSPIF) if(!--guard) return false;
    return !SSPCON2bits.ACKSTAT;
}
static void control(void) {
    const char *p; uint32_t a,b,c;
    if(!rx_ready) return;
    p=(const char*)rx;
    if(frame_valid(p)&&p[2]==',') {
        if(p[1]=='T') { p+=3; if(read_u32(&p,&a,'*')) (void)utc_mirror_set(&clock_mirror,a); }
        else if(p[1]=='S') {
            p+=3;
            if(read_u32(&p,&a,',')&&read_u32(&p,&b,',')&&read_u32(&p,&c,'*')&&a<=1&&b<=1) {
                wifi_ok=(uint8_t)a; cloud_ok=(uint8_t)b; last_send_uptime=c; status_age=0;
            }
        }
    }
    rx_used=0; rx_ready=0;
}
static bool dht_wait(uint8_t level) {
    uint8_t wait=120;
    while(DHT_PIN==level) { if(!--wait) return false; __delay_us(1); }
    return true;
}
static bool dht_read(uint16_t *temperature,uint16_t *humidity) {
    uint8_t d[5]={0,0,0,0,0},i,j; bool ok=false;
    PORTBbits.RB0=0; DHT_DIR=0; __delay_ms(18); DHT_DIR=1;
    /* Disable RX IRQ only for the timing-sensitive ~5 ms response. UART overruns recover in ISR. */
    PIE1bits.RCIE=0;
    __delay_us(10);
    /* Wait for the sensor's initial high-to-low edge before its 80us response. */
    if(!dht_wait(1)||!dht_wait(0)||!dht_wait(1)) goto end;
    for(i=0;i<5;++i) for(j=0;j<8;++j) {
        if(!dht_wait(0)) goto end;
        __delay_us(35); d[i]<<=1; if(DHT_PIN) d[i]|=1;
        if(!dht_wait(1)) goto end;
    }
    if((uint8_t)(d[0]+d[1]+d[2]+d[3])!=d[4]||d[0]>100||d[2]>50||d[1]>9||d[3]>9) goto end;
    *humidity=(uint16_t)d[0]*10+d[1]; *temperature=(uint16_t)d[2]*10+d[3]; ok=true;
end: PIE1bits.RCIE=1; return ok;
}

/* 5x7 font in program memory, streamed directly to OLED: no 1024-byte framebuffer. */
static const uint8_t glyphs[][5]={
{0x3E,0x51,0x49,0x45,0x3E},{0,0x42,0x7F,0x40,0},{0x42,0x61,0x51,0x49,0x46},{0x21,0x41,0x45,0x4B,0x31},{0x18,0x14,0x12,0x7F,0x10},
{0x27,0x45,0x45,0x45,0x39},{0x3C,0x4A,0x49,0x49,0x30},{0x01,0x71,0x09,0x05,0x03},{0x36,0x49,0x49,0x49,0x36},{0x06,0x49,0x49,0x29,0x1E},
{0x7E,0x11,0x11,0x11,0x7E},{0x7F,0x49,0x49,0x49,0x36},{0x3E,0x41,0x41,0x41,0x22},{0x7F,0x41,0x41,0x22,0x1C},{0x7F,0x49,0x49,0x49,0x41},
{0x7F,0x09,0x09,0x09,0x01},{0x3E,0x41,0x49,0x49,0x7A},{0x7F,0x08,0x08,0x08,0x7F},{0,0x41,0x7F,0x41,0},{0x20,0x40,0x41,0x3F,0x01},
{0x7F,0x08,0x14,0x22,0x41},{0x7F,0x40,0x40,0x40,0x40},{0x7F,0x02,0x0C,0x02,0x7F},{0x7F,0x04,0x08,0x10,0x7F},{0x3E,0x41,0x41,0x41,0x3E},
{0x7F,0x09,0x09,0x09,0x06},{0x3E,0x41,0x51,0x21,0x5E},{0x7F,0x09,0x19,0x29,0x46},{0x46,0x49,0x49,0x49,0x31},{1,1,0x7F,1,1},
{0x3F,0x40,0x40,0x40,0x3F},{0x1F,0x20,0x40,0x20,0x1F},{0x3F,0x40,0x38,0x40,0x3F},{0x63,0x14,0x08,0x14,0x63},{7,8,0x70,8,7},{0x61,0x51,0x49,0x45,0x43}
};
static bool oled_cmd(uint8_t command) {
    bool ok=i2c_start()&&i2c_write(OLED_ADDR<<1)&&i2c_write(0)&&i2c_write(command);
    i2c_stop(); return ok;
}
static void oled_init(void) {
    static const uint8_t commands[]={0xAE,0xD5,0x80,0xA8,0x3F,0xD3,0,0x40,0x8D,0x14,0x20,0x02,0xA1,0xC8,0xDA,0x12,0x81,0x7F,0xD9,0xF1,0xDB,0x40,0xA4,0xA6,0xAF};
    uint8_t i; oled_ready=false;
    for(i=0;i<sizeof commands;++i) if(!oled_cmd(commands[i])) return;
    oled_ready=true;
}
static uint8_t glyph(char c,uint8_t column) {
    if(c>='0'&&c<='9') return glyphs[c-'0'][column];
    if(c>='A'&&c<='Z') return glyphs[c-'A'+10][column];
    if(c==':') return column==2?0x36:0;
    if(c=='.') return column==2?0x60:0;
    if(c=='-') return 0x08;
    if(c=='/') return (uint8_t)(0x40>>column);
    if(c=='%') { static const uint8_t percent[]={0x63,0x13,0x08,0x64,0x63}; return percent[column]; }
    return 0;
}
static void oled_line(uint8_t row,const char *text) {
    uint8_t col,c;
    if(!oled_cmd(0xB0+row)||!oled_cmd(0)||!oled_cmd(0x10)) return;
    if(!i2c_start()||!i2c_write(OLED_ADDR<<1)||!i2c_write(0x40)) goto end;
    for(col=0;col<21;++col) {
        char value=*text?*text++:' ';
        for(c=0;c<5;++c) if(!i2c_write(glyph(value,c))) goto end;
        if(!i2c_write(0)) goto end;
    }
    (void)i2c_write(0); (void)i2c_write(0);
end: i2c_stop();
}
static void decimal(char *p,uint16_t n,uint8_t width) { while(width) { p[--width]=(char)('0'+n%10); n/=10; } }
static void screen(uint8_t page,uint16_t temp,uint16_t hum,uint8_t flags,uint32_t epoch) {
    char line[22]; utc_time_t t;
    /* ESP32 may enable the TXS after PIC boot. Retry instead of losing OLED permanently. */
    if(!oled_ready) { oled_init(); if(!oled_ready) return; }
    oled_line(0,page?"NETWORK STATUS":"ENVIRONMENT MONITOR");
    if(!page) {
        if(flags&1) {
            const char *s="TEMP: 00.0 C"; uint8_t i; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line+6,temp/10,2); line[9]=(char)('0'+temp%10); oled_line(2,line);
            s="HUM:  000.0 %"; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line+6,hum/10,3); line[10]=(char)('0'+hum%10); oled_line(4,line);
        } else { oled_line(2,"SENSOR ERROR"); oled_line(4,"CHECK DHT11"); }
        if((flags&2)&&epoch_to_calendar(epoch+LOCAL_OFFSET_SECONDS,&t)) {
            uint8_t i; const char *s="0000-00-00 00:00:00"; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line,t.year,4); decimal(line+5,t.month,2); decimal(line+8,t.day,2);
            decimal(line+11,t.hour,2); decimal(line+14,t.minute,2); decimal(line+17,t.second,2); oled_line(6,line);
        } else oled_line(6,"TIME NOT SYNCED");
    } else {
        oled_line(2,wifi_ok?"WIFI: CONNECTED":"WIFI: OFFLINE");
        oled_line(4,cloud_ok?"CLOUD: HTTP OK":"CLOUD: WAIT / ERROR");
        if(last_send_uptime&&epoch_to_calendar(last_send_uptime+LOCAL_OFFSET_SECONDS,&t)) {
            uint8_t i; const char *s="LAST SEND: 00:00:00"; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line+11,t.hour,2); decimal(line+14,t.minute,2); decimal(line+17,t.second,2); oled_line(6,line);
        } else oled_line(6,"LAST SEND: NONE");
    }
    oled_line(1,""); oled_line(3,""); oled_line(5,""); oled_line(7,"BTN: CHANGE PAGE");
}
void main(void) {
    uint16_t tick=0,temp=0,humidity=0;
    uint32_t seq=0,epoch=0;
    uint8_t page=0,debounce=0,flags=0,refresh=1;
    ADCON1=0x06; TRISB=0xFF; PORTB=0; TRISC=0x98;
    SSPCON=0x28; SSPADD=49; SSPSTAT=0x80; /* I2C 100 kHz. */
    TXSTA=0x24; RCSTA=0x90; SPBRG=129;
    PIE1bits.RCIE=1; INTCONbits.PEIE=1; INTCONbits.GIE=1;
    __delay_ms(100); oled_init();
    for(;;) {
        control();
        utc_mirror_tick(&clock_mirror);
        if(status_age<600) ++status_age;
        else { wifi_ok=0; cloud_ok=0; }
        if(!PAGE_BUTTON) {
            if(debounce<6) ++debounce;
            if(debounce==5) { page^=1; refresh=1; }
        } else debounce=0;
        if(!tick) {
            flags=0; epoch=0; temp=0; humidity=0;
            if(dht_read(&temp,&humidity)) flags|=1;
            if(utc_mirror_get(&clock_mirror,&epoch)) flags|=2;
            measurement(++seq,epoch,temp,humidity,flags); refresh=1;
        }
        if(refresh) { screen(page,temp,humidity,flags,epoch); refresh=0; }
        __delay_ms(10); if(++tick>=200) tick=0;
    }
}
