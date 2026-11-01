#ifndef ENV_CLOCK_H
#define ENV_CLOCK_H
#include <stdint.h>
#include <stdbool.h>
/* A display mirror, not a battery-backed or free-running clock. Refreshed by ESP32. */
typedef struct { uint32_t epoch; uint16_t age_ticks; bool valid; } utc_mirror_t;
static inline bool utc_mirror_set(utc_mirror_t *clock,uint32_t epoch) {
    clock->valid=epoch>=1704067200UL&&epoch<4102444800UL;
    clock->epoch=clock->valid?epoch:0;
    clock->age_ticks=0;
    return clock->valid;
}
static inline void utc_mirror_tick(utc_mirror_t *clock) {
    if(clock->age_ticks<600) ++clock->age_ticks;
    if(clock->age_ticks>=600) clock->valid=false;
}
static inline bool utc_mirror_get(const utc_mirror_t *clock,uint32_t *epoch) {
    *epoch=clock->valid?clock->epoch:0;
    return clock->valid;
}
#endif
