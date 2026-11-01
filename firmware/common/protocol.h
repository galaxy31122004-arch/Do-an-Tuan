#ifndef ENV_PROTOCOL_H
#define ENV_PROTOCOL_H
#include <stdint.h>
#include <stdbool.h>

typedef struct { uint32_t sequence, epoch; int16_t temperature10; uint16_t humidity10; uint8_t flags; } measurement_t;
typedef struct { uint16_t year; uint8_t month, day, hour, minute, second; } rtc_time_t;
/* Flags: bit 0 = valid sensor, bit 1 = valid UTC RTC. CRC-8/SMBUS detects line errors, not attacks. */
static uint8_t crc8_update(uint8_t crc,uint8_t value) {
    uint8_t bit; crc^=value;
    for(bit=0;bit<8;++bit) crc=(crc&0x80)?(uint8_t)((crc<<1)^0x07):(uint8_t)(crc<<1);
    return crc;
}
static uint8_t frame_crc(const char *p) { uint8_t c=0; while(*p) c=crc8_update(c,(uint8_t)*p++); return c; }
static int8_t hex_digit(char c) {
    if(c>='0'&&c<='9') return c-'0';
    if(c>='A'&&c<='F') return c-'A'+10;
    if(c>='a'&&c<='f') return c-'a'+10;
    return -1;
}
static bool frame_valid(const char *p) {
    uint8_t crc=0; int8_t a,b;
    if(*p++!='$') return false;
    while(*p && *p!='*') crc=crc8_update(crc,(uint8_t)*p++);
    if(*p++!='*') return false;
    if(!p[0]||!p[1]) return false;
    a=hex_digit(p[0]); b=hex_digit(p[1]);
    return a>=0&&b>=0&&p[2]==0&&crc==(uint8_t)((a<<4)|b);
}
static bool read_u32(const char **p, uint32_t *v, char end) {
    uint32_t x=0; const char *s=*p;
    if(*s<'0'||*s>'9') return false;
    while(*s>='0'&&*s<='9') {
        uint8_t d=(uint8_t)(*s++-'0');
        if(x>429496729UL || (x==429496729UL&&d>5)) return false;
        x=x*10+d;
    }
    if(*s!=end) return false;
    *p=s+1; *v=x; return true;
}
static bool parse_measurement(const char *s, measurement_t *m) {
    uint32_t v; bool negative;
    if(!frame_valid(s)||s[1]!='M'||s[2]!=',') return false;
    s+=3;
    if(!read_u32(&s,&m->sequence,',')||!read_u32(&s,&m->epoch,',')) return false;
    negative=*s=='-'; if(negative) ++s;
    if(!read_u32(&s,&v,',')||v>800||(negative&&v>400)) return false;
    m->temperature10=negative?-(int16_t)v:(int16_t)v;
    if(!read_u32(&s,&v,',')||v>1000) return false;
    m->humidity10=(uint16_t)v;
    if(!read_u32(&s,&v,'*')||v>3) return false;
    m->flags=(uint8_t)v;
    if((m->flags&2)&&(m->epoch<946684800UL||m->epoch>=4102444800UL)) return false;
    return true;
}
static uint8_t month_days(uint16_t y,uint8_t m) {
    if(m==2) return (y%4==0)?29:28; /* Supported range 2000..2099. */
    return (m==4||m==6||m==9||m==11)?30:31;
}
static inline bool rtc_to_epoch(const rtc_time_t *t,uint32_t *out) {
    uint32_t days=10957; uint16_t y; uint8_t m;
    if(t->year<2000||t->year>2099||t->month<1||t->month>12||t->day<1||t->day>month_days(t->year,t->month)||t->hour>23||t->minute>59||t->second>59) return false;
    for(y=2000;y<t->year;++y) days+=y%4==0?366:365;
    for(m=1;m<t->month;++m) days+=month_days(t->year,m);
    *out=((days+t->day-1)*24+t->hour)*3600UL+t->minute*60UL+t->second;
    return true;
}
static inline bool epoch_to_rtc(uint32_t e,rtc_time_t *t) {
    uint32_t days; uint16_t n;
    if(e<946684800UL||e>=4102444800UL) return false;
    t->second=e%60; e/=60; t->minute=e%60; e/=60; t->hour=e%24;
    days=e/24-10957; t->year=2000;
    while(days>=(n=t->year%4==0?366:365)) { days-=n; ++t->year; }
    t->month=1;
    while(days>=(n=month_days(t->year,t->month))) { days-=n; ++t->month; }
    t->day=(uint8_t)days+1; return true;
}
#endif
