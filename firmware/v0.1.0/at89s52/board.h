#ifndef BOARD_H
#define BOARD_H
#define FOSC_HZ 11059200UL
#define OLED_ADDR 0x3C
#define LOCAL_OFFSET_SECONDS 25200UL
#define DHT_PIN P3_2 /* DIP40 pin 12 */
#define PAGE_BUTTON P3_3 /* pin 13, active low */
#define I2C_SDA P1_0 /* pin 1 */
#define I2C_SCL P1_1 /* pin 2 */
/* RXD=P3.0 pin10, TXD=P3.1 pin11; EA/VPP pin31 tied to +5V. */
#endif
