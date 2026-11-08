#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../firmware/v0.1.0/common/protocol.h"
#include "../firmware/v0.1.0/common/clock.h"

int main(void) {
    assert(frame_crc("123456789")==0xF4); /* CRC-8/SMBUS published check vector. */
    measurement_t m;
    char wire[96];
    const char *payload = "M,42,1761955200,253,641,3";
    snprintf(wire, sizeof wire, "$%s*%02X", payload, frame_crc(payload));
    assert(parse_measurement(wire, &m));
    assert(m.sequence == 42 && m.epoch == 1761955200UL);
    assert(m.temperature10 == 253 && m.humidity10 == 641 && m.flags == 3);
    char swapped[96]; strcpy(swapped,wire);
    char *digits=strstr(swapped,",253,");
    assert(digits); digits[1]='5'; digits[2]='2';
    assert(!parse_measurement(swapped,&m));
    wire[strlen(wire)-1] = wire[strlen(wire)-1] == '0' ? '1' : '0';
    assert(!parse_measurement(wire, &m));
    const char *bad[] = {"M,1,1761955200,99999,500,3", "M,1,1761955200,250,1001,3", "M,1,1761955200,250,500,7", "M,1,1761955200,250,500,3,9", "M,1,4294967296,250,500,3", "M,-1,1761955200,250,500,3"};
    for(unsigned i=0; i<sizeof bad/sizeof bad[0]; ++i) {
        snprintf(wire,sizeof wire,"$%s*%02X",bad[i],frame_crc(bad[i]));
        assert(!parse_measurement(wire,&m));
    }
    assert(!parse_measurement("$M*00",&m));
    assert(!parse_measurement("",&m));
    utc_time_t t = {2024,2,29,23,59,59}, back;
    uint32_t epoch;
    assert(calendar_to_epoch(&t,&epoch));
    assert(epoch_to_calendar(epoch,&back));
    assert(back.year==2024 && back.month==2 && back.day==29 && back.second==59);
    t.year=2023; assert(!calendar_to_epoch(&t,&epoch));
    t.year=2024; t.month=13; assert(!calendar_to_epoch(&t,&epoch));
    t.month=1; t.day=1; t.hour=24; assert(!calendar_to_epoch(&t,&epoch));
    assert(!epoch_to_calendar(0,&back));
    utc_mirror_t clock={0}; uint32_t current=123;
    assert(!utc_mirror_get(&clock,&current));
    assert(utc_mirror_set(&clock,1761955200UL));
    assert(utc_mirror_get(&clock,&current)&&current==1761955200UL);
    for(unsigned i=0;i<599;++i) utc_mirror_tick(&clock);
    assert(utc_mirror_get(&clock,&current));
    utc_mirror_tick(&clock); assert(!utc_mirror_get(&clock,&current));
    assert(utc_mirror_set(&clock,1761955201UL));
    assert(!utc_mirror_set(&clock,0));
    assert(!utc_mirror_get(&clock,&current));
    puts("PASS: checksums, malformed/overflow frames, flags, calendar boundaries");
    return 0;
}
