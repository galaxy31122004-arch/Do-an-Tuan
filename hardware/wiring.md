# Sơ đồ nối dây — bản lắp mạch thật

Đối chiếu với `firmware/v0.2.0/at89s52/board.h` và `firmware/v0.2.0/esp32/include/settings.h`. Số chân AT89S52 áp dụng **DIP-40**; board mạng là **ESP32-C3 SuperMini, hai hàng chân 1x8**, tra theo nhãn GPIO trên hàng mua. Đây là hướng dẫn kết nối, chưa phải bộ PCB sản xuất đã ERC/DRC.

## 1. Nguồn và khối AT89S52

| Kết nối | Đi đến |
|---|---|
| J1 jack DC tâm (+) → D2 1N4007 anode | Cathode D2 = VIN: C14 100 µF + C15 330 nF xuống GND, vào LM7805 IN |
| U7 LM7805 OUT | Rail +5 V; C16 100 nF sát chân OUT |
| U7 LM7805 GND / tab | GND; tab vít M3 xuống vùng đồng GND làm tản nhiệt |
| J1 vỏ (−) | GND chung toàn mạch; chân switch của jack để trống |
| AT89S52 VCC chân 40 | +5 V; C1 100 nF giữa chân 40/20 |
| AT89S52 GND chân 20 | GND |
| AT89S52 XTAL1 chân 19 ↔ Y1 11,0592 MHz ↔ XTAL2 chân 18 | C9/C10 22 pF từ từng đầu thạch anh xuống GND |
| AT89S52 RST chân 9 | R1 10 kΩ xuống GND; SW2 từ RST lên +5 V; C2 10 µF cực + lên +5 V, cực - vào RST |
| AT89S52 P3.3 chân 13 | SW1 xuống GND; R3 10 kΩ lên +5 V |
| ESP32 chân 5V/VIN theo board | +5 V, không phải chân 3V3 |
| ESP32 3V3 | Rail 3,3 V cấp OLED và TXS0108E VCCA |
| TXS0108E VCCB / VCCA | +5 V / 3,3 V; C3/C13 100 nF lọc từng rail sang GND |
| TXS0108E OE | ESP32 GPIO6; R4 100 kΩ từ OE xuống GND |
| C6 100 nF, C7 470 µF | +5 V–GND sát ESP32 |
| C11 10 µF | +5 V–GND gần AT89S52 |
| +5 V → R10 1 kΩ → anode D1 | Cathode LED xuống GND |
| TP1 / TP2 / TP3 | +5 V / 3,3 V / GND |

**Nguồn LM7805:** dùng adapter **7,5–9 V / 1 A**. Dòng tải ước tính khoảng 250 mA (ESP32 Wi-Fi, relay, AT89S52, OLED), đỉnh tới khoảng 450 mA khi ESP32 phát. Với 9 V, LM7805 tỏa khoảng (9 − 0,7 − 5) × 0,25 ≈ 0,8 W; với 12 V khoảng 1,6 W, nóng hơn nhiều khi chỉ tản qua PCB. LM7805 nằm ngang, tab vít M3 xuống vùng đồng GND rộng tối thiểu khoảng 25×25 mm, nên có ở cả hai mặt nối bằng nhiều via; bôi keo tản nhiệt. Tab của 7805 là GND nên không cần đệm cách điện. Không cắm USB vào ESP32 khi đang cấp nguồn jack.

EA/VPP chân 31 nối thẳng +5 V để chạy Flash trong; PSEN chân 29 và ALE chân 30 để hở. P0 không dùng để hở (P0 cần pull-up nếu sử dụng). Các chân I/O còn lại không dùng để NC; không nối ngẫu nhiên vào nguồn. Nút 4 chân tactile có hai cặp nối sẵn: chọn hai chân khác tiếp điểm, đo thông mạch trước khi hàn.

## 2. DHT11 rời

Nhìn chính diện lưới cảm biến và chân hướng xuống, xác minh lại nhãn/datasheet hàng mua.

| DHT11 | Kết nối |
|---|---|
| 1 VCC | +5 V |
| 2 DATA | AT89S52 P3.2 chân 12; R2 4,7 kΩ kéo DATA lên +5 V |
| 3 NC | Để hở |
| 4 GND | GND |

C12 100 nF đặt sát chân 1/4 của DHT11 để lọc nguồn cảm biến.

Không áp dụng thứ tự này cho module 3 chân. Đặt cảm biến xa nguồn nhiệt ESP32 và bộ nguồn.

## 3. Nguồn thời gian NTP từ ESP32

Không lắp module thời gian thực hoặc pin dự phòng. ESP32 lấy UTC từ NTP, duy trì giờ khi còn nguồn và gửi frame T cho AT89S52 khoảng mỗi giây. AT89S52 hiển thị UTC+7; chưa có giờ hoặc UART quá hạn sẽ báo TIME NOT SYNCED. Sau mất điện cần đồng bộ lại qua Internet.

## 4. OLED và module TXS0108E

| Kênh | Phía A: 3,3 V | Phía B: 5 V |
|---|---|---|
| A1/B1 — SDA | OLED SDA | AT89S52 P1.0/1 |
| A2/B2 — SCL | OLED SCL | AT89S52 P1.1/2 |
| A3/B3 — AT89S52 phát | ESP32 GPIO4/RX1 | AT89S52 P3.1/TX/11 |
| A4/B4 — ESP32 phát | ESP32 GPIO5/TX1 | AT89S52 P3.0/RX/10 |
| A5–A8/B5–B8 | NC | NC |
| OLED VCC/GND | 3,3 V/GND; C5 100 nF + C8 10 µF | — |

Đấu module theo nhãn A/B và VCCA/VCCB/OE/GND, không dùng số chân IC trần để suy ra header. J5A/J5B dự kiến hai hàng 1x10, xác minh module thực tế trước khi làm PCB. OLED mặc định `0x3C`; đổi `OLED_ADDR` nếu màn dùng `0x3D`.

OE=GPIO6, R4 100 kΩ kéo xuống GND. ESP32 giữ thấp lúc boot, chờ 100 ms rồi bật mức 3,3 V. Kiểm tra/tháo pull-up hoặc cầu nối kéo cứng OE lên nguồn nếu module có; không đưa 5 V vào GPIO6/OE. AT89S52 thử khởi tạo OLED lại khi TXS chưa bật lúc boot.

TXS có pull-up nội, không lắp R6–R9 của thiết kế cũ. Đối chiếu pull-up đã có trên OLED/module, đo tải bus và giữ dây ngắn. C3/C13 100 nF lọc VCCB/VCCA; xem datasheet TI trong `docs/sources.md`.

## 5. UART hai chiều, 9600 baud 8N1

```text
AT89S52 P3.1/TX/11 → TXS B3 ↔ A3 → ESP32 GPIO4/RX1
AT89S52 P3.0/RX/10 ← TXS B4 ↔ A4 ← ESP32 GPIO5/TX1
TXS VCCB=5V, VCCA=3V3, GND chung, OE=GPIO6 + R4 100k xuống GND
```

Không còn bộ chia áp TX hoặc buffer riêng. Không nối AT89S52 TX thẳng vào GPIO4 hoặc thêm bộ chia áp trên đường đã qua TXS. Dùng đúng sơ đồ SuperMini C3: UART1 RX=GPIO4, TX=GPIO5 và OE=GPIO6.

## 6. Burn-E nạp AT89S52; J3 ISP

Quy trình chính: ngắt nguồn, tháo AT89S52 khỏi SK1, đặt vào đế/adapter tương thích của Burn-E đúng hướng dẫn của phiên bản đang dùng, chọn AT89S52, mở file HEX, nạp và verify. Cắm AT89S52 trở lại khi mạch tắt nguồn. Không suy đoán vị trí chân 1 trên đế ZIF.

J3 dùng khi đã chọn đúng AT89S52 và đối chiếu pinout trong Burn-E. Có thể nạp trên mạch khi chỉ cấp một nguồn target; hoặc nạp ở mạch đế có thạch anh và EA kéo lên 5 V. Đế ZIF trần không có dao động ngoài không đủ cho ISP AT89S52. Thứ tự J3 theo bảng kết nối AT89S hiển thị trong Burn-E 9.00.88: MCLR/RST, VDD, GND, PGD/MISO, PGC/SCK, AUX/MOSI. Kiểm tra chiều đầu cắm thực tế.

| J3 | AT89S52 |
|---|---|
| 1 RST | Chân 9, reset mức cao |
| 2 VCC | Rail +5 V |
| 3 GND | GND |
| 4 MISO | P1.6 chân 7 |
| 5 SCK | P1.7 chân 8 |
| 6 MOSI | P1.5 chân 6 |

Đánh dấu chân 1. Nếu dùng ISP, chọn nguồn target theo hướng dẫn Burn-E; không cấp đồng thời nguồn mạch nạp và adapter nếu không được thiết kế cho phép. AT89S52 dùng reset mức cao 5 V khi ISP; không dùng cấu hình VPP của PIC.

## 6b. Relay K1 qua header J6 (firmware v0.2.0)

| J6 | Kết nối |
|---|---|
| 1 VCC | +5 V |
| 2 GND | GND |
| 3 IN | AT89S52 P2.0 chân 21 |

K1 là module relay 1 kênh 5 V có opto, **kích mức thấp**, nối J6 bằng dây. Module đã có transistor, diode chống ngược và LED; không lắp thêm trên PCB. Chân 8051 kéo xuống mạnh nhưng đẩy lên yếu, nên không dùng module kích mức cao. Lúc khởi động P2.0 ở mức cao nên relay tắt.

Firmware bật relay khi nhiệt độ ≥ 32,0 °C, tắt khi ≤ 30,0 °C, và tắt khi DHT11 lỗi. Ngưỡng đặt trong `firmware/v0.2.0/at89s52/board.h`. Tiếp điểm relay chỉ đóng cắt tải điện áp thấp (quạt 5–12 V) trong phạm vi đồ án; không đưa điện lưới lên PCB. Dòng cuộn dây khoảng 70–90 mA lấy từ rail 5 V; adapter 5 V/2 A vẫn đủ.

## 7. Trình tự kiểm tra trước khi cắm IC

1. Kiểm tra chập 5 V/GND và chiều tụ hóa, pin, IC; cấp nguồn giới hạn dòng.
2. Đo 5 V và 3,3 V, kiểm tra nguồn ESP32 ổn định khi Wi-Fi phát.
3. Nạp/verify AT89S52 bằng Burn-E ngoài mạch rồi cắm AT89S52 khi tắt nguồn. Cắm OLED và ESP32, xác nhận OE=3,3 V sau boot rồi kiểm tra thạch anh và ACK I²C.
4. Gắn DHT11, kiểm tra số đo và nút chuyển trang; quan sát TX AT89S52 bằng USB-UART/logic analyzer đúng mức điện áp.
5. Gắn chuyển mức UART và ESP32; xác nhận gói M/S/T, đồng bộ giờ NTP, rồi mới kiểm tra cloud.

Nguồn: Microchip AT89S52 doc1919 (RSCH-20261101-0011), TI TXS0108E (RSCH-20261101-0005), OLED (RSCH-20261101-0004). Burn-E do người dùng xác nhận; phần mềm đang mở là Burn-E Programmer 9.00.88; xác nhận kết nối phần cứng và pinout hiển thị cho AT89S52 trước khi nạp.
