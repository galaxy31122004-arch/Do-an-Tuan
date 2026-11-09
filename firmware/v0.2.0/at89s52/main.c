/* AT89S52 classic 12T, SDCC mcs51, external 11.0592 MHz crystal. */
#include <8052.h>
#include <stdint.h>
#include <stdbool.h>
#include "board.h"
#define ENV_HOST_ONLY
#include "../common/protocol.h"
#include "../common/clock.h"
/* RX lives in interrupt context; each incoming line fits in 48 bytes. */
static volatile __idata char rx[48];
static volatile uint8_t rx_used=0,rx_ready=0;
static uint8_t wifi_ok=0,cloud_ok=0,relay_on=0;
static uint32_t last_send_uptime=0;
static uint16_t status_age=600;
static uint8_t tx_crc;
static volatile __bit tx_done;
static __idata uint8_t dht_bytes[5];
static __idata uint16_t temp,humidity;
static __idata uint32_t seq,epoch;
static __idata uint8_t flags,page;
static __idata char line[22];
static __idata utc_time_t screen_time;
static bool oled_ready=false;
static utc_mirror_t clock_mirror={0};

void serial_irq(void) __interrupt(4) __using(1) {
    char c;
    if(TI) { TI=0; tx_done=1; }
    if(RI) {
        c=SBUF; RI=0;
        if(rx_ready) return;
        if(c=='$') rx_used=0;
        if(c=='\r') return;
        if(c=='\n') { rx[rx_used]=0; rx_ready=1; }
        else if(rx_used<sizeof(rx)-1) rx[rx_used++]=c;
        else rx_used=0;
    }
}
static void uart_raw(char c) { tx_done=0; SBUF=c; while(!tx_done) {} }
/* Timer0 runs at Fosc/12; round delays upward. UART reception stays enabled. */
static void delay_us(uint16_t us) {
    uint16_t count=us-us/13+1;
    TR0=0; TF0=0; count=(uint16_t)(0-count); TH0=count>>8; TL0=count;
    TR0=1; while(!TF0) {} TR0=0; TF0=0;
}
static void delay_ms(uint16_t ms) { while(ms--) delay_us(1000); }
static void uart_body(char c) { tx_crc=crc8_update(tx_crc,(uint8_t)c); uart_raw(c); }
static void uart_num(uint32_t n) {
    uint32_t divisor=1000000000UL;
    while(divisor>1&&n<divisor) divisor/=10;
    do { uart_body((char)('0'+n/divisor)); n%=divisor; divisor/=10; } while(divisor);
}
static void measurement(void) {
    static const __code char hex[]="0123456789ABCDEF";
    uart_raw('$'); tx_crc=0; uart_body('M'); uart_body(','); uart_num(seq);
    uart_body(','); uart_num(epoch); uart_body(','); uart_num(temp);
    uart_body(','); uart_num(humidity); uart_body(','); uart_num(flags);
    uart_raw('*'); uart_raw(hex[tx_crc>>4]); uart_raw(hex[tx_crc&15]); uart_raw('\n');
}
/* Open-drain P0 (R8/R9 pull-ups): write 1 to release, 0 to pull low. */
static bool scl_release(void) {
    uint8_t guard=255; I2C_SCL=1;
    while(!I2C_SCL) if(!--guard) return false;
    return true;
}
static bool i2c_start(void) {
    I2C_SDA=1; if(!scl_release()) return false;
    delay_us(5); if(!I2C_SDA) return false;
    I2C_SDA=0; delay_us(5); I2C_SCL=0; return true;
}
static void i2c_stop(void) {
    I2C_SDA=0; (void)scl_release(); delay_us(5); I2C_SDA=1; delay_us(5);
}
static bool i2c_write(uint8_t value) {
    uint8_t bitno; bool ack;
    for(bitno=0;bitno<8;++bitno) {
        I2C_SDA=(value&0x80)?1:0; value<<=1; delay_us(5);
        if(!scl_release()) return false;
        delay_us(5); I2C_SCL=0;
    }
    I2C_SDA=1; delay_us(5); if(!scl_release()) return false;
    delay_us(5); ack=!I2C_SDA; I2C_SCL=0; return ack;
}
static void control(void) __reentrant {
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
/* Timing-critical capture is assembly: no C calls/register spills between edges.
 * Fosc/12 = 921600 Hz. 40 ticks separates DHT11 26us and 70us highs.
 * Timer0 timeout 110 ticks (~119us). ES is off throughout capture. */
static bool dht_capture(void) __naked {
    __asm
        mov r0,#_dht_bytes
        mov r5,#5
        clr _TR0
        mov _TH0,#0
        mov _TL0,#0
        setb _TR0
        setb _P3_2
09100$:
        jnb _P3_2,09101$
        lcall 09109$
        jnc 09100$
        sjmp 09110$
09101$:
        mov _TH0,#0
        mov _TL0,#0
09102$:
        jb _P3_2,09103$
        lcall 09109$
        jnc 09102$
        sjmp 09110$
09103$:
        mov _TH0,#0
        mov _TL0,#0
09104$:
        jnb _P3_2,09105$
        lcall 09109$
        jnc 09104$
        sjmp 09110$
09105$:
        mov r6,#8
        mov r7,#0
09106$:
        mov _TH0,#0
        mov _TL0,#0
09107$:
        jb _P3_2,09108$
        lcall 09109$
        jnc 09107$
        sjmp 09110$
09108$:
        mov _TH0,#0
        mov _TL0,#0
09111$:
        jnb _P3_2,09112$
        lcall 09109$
        jnc 09111$
        sjmp 09110$
09112$:
        mov a,_TL0
        clr c
        subb a,#40
        cpl c
        mov a,r7
        rlc a
        mov r7,a
        djnz r6,09106$
        mov @r0,a
        inc r0
        djnz r5,09105$
        clr _TR0
        mov dpl,#1
        ret
09109$:
        mov a,_TH0
        jnz 09113$
        mov a,_TL0
        clr c
        subb a,#110
        cpl c
        ret
09113$:
        setb c
        ret
09110$:
        clr _TR0
        mov dpl,#0
        ret
    __endasm;
}
static bool dht_read(void) {
    bool ok;
    DHT_PIN=0; delay_ms(18);
    /* Drop partial control frame; next ESP32 update resynchronizes via CRC. */
    ES=0; rx_used=0; rx_ready=0;
    ok=dht_capture(); RI=0; ES=1;
    if(!ok||(uint8_t)(dht_bytes[0]+dht_bytes[1]+dht_bytes[2]+dht_bytes[3])!=dht_bytes[4]||dht_bytes[0]>100||dht_bytes[2]>50||dht_bytes[1]>9||dht_bytes[3]>9) return false;
    humidity=(uint16_t)dht_bytes[0]*10+dht_bytes[1];
    temp=(uint16_t)dht_bytes[2]*10+dht_bytes[3]; return true;
}

/* 5x7 font in program memory, streamed directly to OLED: no 1024-byte framebuffer. */
static const __code uint8_t glyphs[][5]={
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
    static const __code uint8_t commands[]={0xAE,0xD5,0x80,0xA8,0x3F,0xD3,0,0x40,0x8D,0x14,0x20,0x02,0xA1,0xC8,0xDA,0x12,0x81,0x7F,0xD9,0xF1,0xDB,0x40,0xA4,0xA6,0xAF};
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
    if(c=='%') { static const __code uint8_t percent[]={0x63,0x13,0x08,0x64,0x63}; return percent[column]; }
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
static void screen(void) __reentrant {
    /* Date scratch storage lives in internal indirect RAM. */
    /* ESP32 may enable the TXS after AT89S52 boot. Retry instead of losing OLED permanently. */
    if(!oled_ready) { oled_init(); if(!oled_ready) return; }
    oled_line(0,page?"NETWORK STATUS":"ENVIRONMENT MONITOR");
    if(!page) {
        if(flags&1) {
            const char *s="TEMP: 00.0 C"; uint8_t i; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line+6,temp/10,2); line[9]=(char)('0'+temp%10); oled_line(2,line);
            s="HUM:  000.0 %"; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line+6,humidity/10,3); line[10]=(char)('0'+humidity%10); oled_line(4,line);
        } else { oled_line(2,"SENSOR ERROR"); oled_line(4,"CHECK DHT11"); }
        oled_line(5,relay_on?"RELAY: ON":"RELAY: OFF");
        if((flags&2)&&epoch_to_calendar(epoch+LOCAL_OFFSET_SECONDS,&screen_time)) {
            uint8_t i; const char *s="0000-00-00 00:00:00"; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line,screen_time.year,4); decimal(line+5,screen_time.month,2); decimal(line+8,screen_time.day,2);
            decimal(line+11,screen_time.hour,2); decimal(line+14,screen_time.minute,2); decimal(line+17,screen_time.second,2); oled_line(6,line);
        } else oled_line(6,"TIME NOT SYNCED");
    } else {
        oled_line(2,wifi_ok?"WIFI: CONNECTED":"WIFI: OFFLINE");
        oled_line(4,cloud_ok?"CLOUD: HTTP OK":"CLOUD: WAIT / ERROR");
        if(last_send_uptime&&epoch_to_calendar(last_send_uptime+LOCAL_OFFSET_SECONDS,&screen_time)) {
            uint8_t i; const char *s="LAST SEND: 00:00:00"; for(i=0;(line[i]=s[i])!=0;++i) {}
            decimal(line+11,screen_time.hour,2); decimal(line+14,screen_time.minute,2); decimal(line+17,screen_time.second,2); oled_line(6,line);
        } else oled_line(6,"LAST SEND: NONE");
    }
    if(page) oled_line(5,"");
    oled_line(1,""); oled_line(3,""); oled_line(7,"BTN: CHANGE PAGE");
}
void main(void) {
    uint16_t tick=0;
    uint8_t debounce=0,refresh=1;
    P1=0xFF; P2=0xFF; P3=0xFF; /* P2.0 high = opto LED off = relay off (also during reset) */
    TMOD=0x21; /* T1 8-bit auto-reload UART; T0 16-bit delay/pulse timer. */
    PCON&=0x7F; TH1=0xFD; TL1=0xFD; SCON=0x50; TI=0; RI=0;
    TR1=1; ES=1; EA=1;
    delay_ms(100); oled_init();
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
            if(dht_read()) {
                flags|=1;
                if(temp>=RELAY_ON_T10) relay_on=1;
                else if(temp<=RELAY_OFF_T10) relay_on=0;
            } else relay_on=0; /* fail safe: no reading, load off */
            RELAY_PIN=relay_on?0:1;
            if(relay_on) flags|=4;
            if(utc_mirror_get(&clock_mirror,&epoch)) flags|=2;
            ++seq; measurement(); refresh=1;
        }
        if(refresh) { screen(); refresh=0; }
        delay_ms(10); if(++tick>=200) tick=0;
    }
}
