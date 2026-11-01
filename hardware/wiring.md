# Sơ đồ nối dây — bản lắp mạch thật

Đối chiếu với `firmware/pic/board.h` và `firmware/esp32/include/settings.h`. Số chân PIC áp dụng **DIP-40**; ESP32 là **WROOM-32 DevKit 30 chân**, tra theo tên chân trên board. Đây là hướng dẫn kết nối, chưa phải bộ PCB sản xuất đã ERC/DRC.

## 1. Nguồn và khối PIC

| Kết nối | Đi đến |
|---|---|
| J1 +5 V → F1 | Rail +5 V sau cầu chì |
| J1 GND | GND chung toàn mạch |
| PIC VDD chân 11, 32 | +5 V; C1/C2 100 nF mỗi cặp VDD/VSS |
| PIC VSS chân 12, 31 | GND |
| PIC OSC1 chân 13 ↔ Y1 20 MHz ↔ OSC2 chân 14 | C9/C10 22 pF từ từng đầu thạch anh xuống GND |
| PIC MCLR chân 1 | R1 10 kΩ lên +5 V; SW2 từ MCLR xuống GND |
| PIC RB1 chân 34 | SW1 xuống GND; R3 10 kΩ lên +5 V |
| ESP32 chân 5V/VIN theo board | +5 V, không phải chân 3V3 |
| ESP32 3V3 | Rail 3,3 V chỉ cấp OLED và hai gate BSS138/pull-up LV |
| C6 100 nF, C7 470 µF | +5 V–GND sát ESP32 |
| C11 10 µF | +5 V–GND gần PIC/RTC |
| +5 V → R10 1 kΩ → anode D1 | Cathode LED xuống GND |
| TP1 / TP2 / TP3 | +5 V / 3,3 V / GND |

Các chân PIC không dùng để NC; không nối ngẫu nhiên vào nguồn. Nút 4 chân tactile có hai cặp nối sẵn: chọn hai chân khác tiếp điểm, đo thông mạch trước khi hàn.

## 2. DHT11 rời

Nhìn chính diện lưới cảm biến và chân hướng xuống, xác minh lại nhãn/datasheet hàng mua.

| DHT11 | Kết nối |
|---|---|
| 1 VCC | +5 V |
| 2 DATA | PIC RB0 chân 33; R2 4,7 kΩ kéo DATA lên +5 V |
| 3 NC | Để hở |
| 4 GND | GND |

C12 100 nF đặt sát chân 1/4 của DHT11 để lọc nguồn cảm biến.

Không áp dụng thứ tự này cho module 3 chân. Đặt cảm biến xa nguồn nhiệt ESP32 và bộ nguồn.

## 3. RTC DS1307 rời

| DS1307 DIP-8 | Kết nối |
|---|---|
| 1 X1, 2 X2 | Hai đầu Y2 32,768 kHz CL 12,5 pF; không thêm tụ tải ngoài |
| 3 VBAT | Cực + BH1/CR2032; cực − đế pin nối GND |
| 4 GND | GND |
| 5 SDA | SDA_HV, PIC RC4 chân 23 |
| 6 SCL | SCL_HV, PIC RC3 chân 18 |
| 7 SQW/OUT | NC |
| 8 VCC | +5 V; C4 100 nF sang GND |

DS1307 lưu **UTC**. ESP32 lấy NTP và gửi thời gian cho PIC; OLED hiển thị UTC+7. Pin chỉ giữ RTC, không cấp cho PIC/ESP32. Không có mạch sạc pin trong thiết kế.

## 4. OLED và chuyển mức I²C

| Net | Phía 5 V | Phía 3,3 V |
|---|---|---|
| SDA | PIC RC4 chân 23 + DS1307 chân 5 + Q1 D chân 3; R6 4,7 kΩ lên 5 V | Q1 S chân 2 + OLED SDA; R8 4,7 kΩ lên 3,3 V |
| SCL | PIC RC3 chân 18 + DS1307 chân 6 + Q2 D chân 3; R7 4,7 kΩ lên 5 V | Q2 S chân 2 + OLED SCL; R9 4,7 kΩ lên 3,3 V |
| Gate | Q1/Q2 G chân 1 đều nối 3,3 V | Không nối gate lên 5 V |
| OLED VCC/GND | — | 3,3 V/GND; C5 100 nF và C8 10 µF |

Pinout BSS138 SOT-23 cần đối chiếu hãng mua. Địa chỉ 7-bit mặc định firmware: OLED `0x3C`, DS1307 `0x68`; nếu OLED dùng `0x3D`, đổi `OLED_ADDR`. Kiểm tra pull-up đã gắn trên OLED trước khi lắp R8/R9. Không đưa trực tiếp SDA/SCL 5 V sang module OLED chưa xác minh mức logic.

## 5. UART hai chiều, 9600 baud 8N1

```text
PIC RC6/TX chân 25 ─ R4 10k ─┬─ ESP32 GPIO16/RX2
                              R5 20k
                               │
                              GND

ESP32 GPIO17/TX2 ─ U4 pin 2 (1A)
                   U4 pin 3 (1Y) ─ PIC RC7/RX chân 26
U4 pin 1 (/1OE) = GND; pin 14 = +5V; pin 7 = GND
```

U4 là **SN74AHCT125**, không phải HC125. C3 100 nF sát chân 14/7. Các /OE không dùng (4,10,13) nối +5 V; input 5,9,12 nối GND; output 6,8,11 để NC. Không nối PIC TX thẳng vào GPIO16. Không dùng module ESP32-WROVER vì GPIO16/17 có thể dành cho PSRAM.

## 6. ICSP nạp PIC

| J3 | PIC |
|---|---|
| 1 VPP/MCLR | Chân 1 |
| 2 VDD sense | Rail +5 V |
| 3 GND | GND |
| 4 PGD | RB7 chân 40 |
| 5 PGC | RB6 chân 39 |
| 6 AUX | NC |

Đánh dấu chân 1. Không nhấn reset khi nạp. Chỉ để một thiết bị cấp nguồn; nếu dùng nguồn mạch ngoài, PICkit chỉ sense VDD. Không cho VPP đi vào ESP32/OLED.

## 7. Trình tự kiểm tra trước khi cắm IC

1. Kiểm tra chập 5 V/GND và chiều tụ hóa, pin, IC; cấp nguồn giới hạn dòng.
2. Đo 5 V và 3,3 V, kiểm tra nguồn ESP32 ổn định khi Wi-Fi phát.
3. Cắm/nạp PIC, kiểm tra thạch anh; cắm RTC và OLED, xác nhận ACK I²C.
4. Gắn DHT11, kiểm tra số đo và nút chuyển trang; quan sát TX PIC bằng USB-UART/logic analyzer đúng mức điện áp.
5. Gắn chuyển mức UART và ESP32; xác nhận gói M/S/T, đồng bộ RTC, rồi mới kiểm tra cloud.

Nguồn tra cứu: Microchip DS39582C và TI SN74AHCT125, đã ghi trong ledger RSCH-20261101-0002; OLED theo RSCH-20261101-0004. Datasheet và tài liệu tham khảo được liệt kê trong `docs/sources.md`.
