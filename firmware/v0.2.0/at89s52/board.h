#ifndef BOARD_H
#define BOARD_H
#define FOSC_HZ 11059200UL
#define OLED_ADDR 0x3C
#define LOCAL_OFFSET_SECONDS 25200UL
#define DHT_PIN P3_2 /* DIP40 pin 12 */
#define PAGE_BUTTON P3_3 /* pin 13, active low */
#define I2C_SDA P0_3 /* pin 36, open-drain: R8 10k pull-up */
#define I2C_SCL P0_4 /* pin 35, open-drain: R9 10k pull-up */
#define RELAY_PIN P2_0 /* pin 21 -> PC817 LED cathode; low = relay on, high = off */
#define RELAY_ON_T10 320 /* switch on at >= 32.0 C */
#define RELAY_OFF_T10 300 /* switch off at <= 30.0 C (hysteresis) */
/* RXD=P3.0 pin10, TXD=P3.1 pin11; EA/VPP pin31 tied to +5V. */
#endif
