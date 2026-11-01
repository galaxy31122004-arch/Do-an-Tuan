# Sơ đồ nối dây — bản lắp mạch thật

Đối chiếu với `firmware/pic/board.h` và `firmware/esp32/include/settings.h`. Số chân PIC áp dụng **DIP-40**; board mạng là **ESP32-C3 SuperMini, hai hàng chân 1x8**, tra theo nhãn GPIO trên hàng mua. Đây là hướng dẫn kết nối, chưa phải bộ PCB sản xuất đã ERC/DRC.

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
| ESP32 3V3 | Rail 3,3 V cấp OLED và TXS0108E VCCA |
| TXS0108E VCCB / VCCA | +5 V / 3,3 V; C3/C13 100 nF lọc từng rail sang GND |
| TXS0108E OE | ESP32 GPIO6; R4 100 kΩ từ OE xuống GND |
| C6 100 nF, C7 470 µF | +5 V–GND sát ESP32 |
| C11 10 µF | +5 V–GND gần PIC |
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

## 3. Nguồn thời gian NTP từ ESP32

Không lắp module thời gian thực hoặc pin dự phòng. ESP32 lấy UTC từ NTP, duy trì giờ khi còn nguồn và gửi frame T cho PIC khoảng mỗi giây. PIC hiển thị UTC+7; chưa có giờ hoặc UART quá hạn sẽ báo TIME NOT SYNCED. Sau mất điện cần đồng bộ lại qua Internet.

## 4. OLED và module TXS0108E

| Kênh | Phía A: 3,3 V | Phía B: 5 V |
|---|---|---|
| A1/B1 — SDA | OLED SDA | PIC RC4/23 |
| A2/B2 — SCL | OLED SCL | PIC RC3/18 |
| A3/B3 — PIC phát | ESP32 GPIO4/RX2 | PIC RC6/TX/25 |
| A4/B4 — ESP32 phát | ESP32 GPIO5/TX2 | PIC RC7/RX/26 |
| A5–A8/B5–B8 | NC | NC |
| OLED VCC/GND | 3,3 V/GND; C5 100 nF + C8 10 µF | — |

Đấu module theo nhãn A/B và VCCA/VCCB/OE/GND, không dùng số chân IC trần để suy ra header. J5A/J5B dự kiến hai hàng 1x10, xác minh module thực tế trước khi làm PCB. OLED mặc định `0x3C`; đổi `OLED_ADDR` nếu màn dùng `0x3D`.

OE=GPIO6, R4 100 kΩ kéo xuống GND. ESP32 giữ thấp lúc boot, chờ 100 ms rồi bật mức 3,3 V. Kiểm tra/tháo pull-up hoặc cầu nối kéo cứng OE lên nguồn nếu module có; không đưa 5 V vào GPIO6/OE. PIC thử khởi tạo OLED lại khi TXS chưa bật lúc boot.

TXS có pull-up nội, không lắp R6–R9 của thiết kế cũ. Đối chiếu pull-up đã có trên OLED/module, đo tải bus và giữ dây ngắn. C3/C13 100 nF lọc VCCB/VCCA; xem datasheet TI trong `docs/sources.md`.

## 5. UART hai chiều, 9600 baud 8N1

```text
PIC RC6/TX/25 → TXS B3 ↔ A3 → ESP32 GPIO4/RX2
PIC RC7/RX/26 ← TXS B4 ↔ A4 ← ESP32 GPIO5/TX2
TXS VCCB=5V, VCCA=3V3, GND chung, OE=GPIO6 + R4 100k xuống GND
```

Không còn bộ chia áp TX hoặc buffer riêng. Không nối PIC TX thẳng vào GPIO4 hoặc thêm bộ chia áp trên đường đã qua TXS. Dùng đúng sơ đồ SuperMini C3: UART1 RX=GPIO4, TX=GPIO5 và OE=GPIO6.

## 6. Burn-E nạp PIC; J3 là header dịch vụ dự phòng

Quy trình chính: ngắt nguồn, tháo PIC khỏi SK1, đặt vào đế/adapter tương thích của Burn-E đúng hướng dẫn của phiên bản đang dùng, chọn PIC16F877A, mở file HEX, nạp và verify. Cắm PIC trở lại khi mạch tắt nguồn. Không suy đoán vị trí chân 1 trên đế ZIF.

J3 chỉ dùng nếu bản Burn-E đó hỗ trợ ICSP và đã đối chiếu pinout cáp. Thứ tự dưới đây là quy ước PCB, không phải khẳng định thứ tự chân đầu cáp Burn-E.

| J3 | PIC |
|---|---|
| 1 VPP/MCLR | Chân 1 |
| 2 VDD | Rail +5 V |
| 3 GND | GND |
| 4 PGD | RB7 chân 40 |
| 5 PGC | RB6 chân 39 |
| 6 AUX | NC |

Đánh dấu chân 1. Nếu dùng ICSP, chọn nguồn target theo hướng dẫn Burn-E; không cấp đồng thời nguồn mạch nạp và adapter nếu không được thiết kế cho phép. Không cho VPP đi vào ESP32/OLED. Không coi Burn-E là bộ debug trực tiếp trong MPLAB.

## 7. Trình tự kiểm tra trước khi cắm IC

1. Kiểm tra chập 5 V/GND và chiều tụ hóa, pin, IC; cấp nguồn giới hạn dòng.
2. Đo 5 V và 3,3 V, kiểm tra nguồn ESP32 ổn định khi Wi-Fi phát.
3. Nạp/verify PIC bằng Burn-E ngoài mạch rồi cắm PIC khi tắt nguồn. Cắm OLED và ESP32, xác nhận OE=3,3 V sau boot rồi kiểm tra thạch anh và ACK I²C.
4. Gắn DHT11, kiểm tra số đo và nút chuyển trang; quan sát TX PIC bằng USB-UART/logic analyzer đúng mức điện áp.
5. Gắn chuyển mức UART và ESP32; xác nhận gói M/S/T, đồng bộ giờ NTP, rồi mới kiểm tra cloud.

Nguồn: Microchip DS39582C (RSCH-20261101-0002), TI TXS0108E (RSCH-20261101-0005), OLED (RSCH-20261101-0004). Burn-E do người dùng xác nhận; chưa có model/pinout cáp cụ thể nên thao tác theo đúng phiên bản đang sở hữu.
