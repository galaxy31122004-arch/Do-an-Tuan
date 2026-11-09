# CHƯƠNG 2. THIẾT KẾ PHẦN CỨNG

## 2.1. Yêu cầu thiết kế

Phần cứng cần đáp ứng các yêu cầu sau:

- Cấp nguồn từ adapter 12 V một chiều, qua jack DC hoặc cầu đấu (domino); tạo nguồn 5 V cho phần điều khiển và 3,3 V cho phần mạng, hiển thị.
- Đo nhiệt độ, độ ẩm bằng DHT11; hiển thị trên OLED; chuyển trang bằng nút nhấn.
- Trao đổi dữ liệu giữa AT89S52 (5 V) và ESP32-C3 (3,3 V) an toàn về mức điện áp.
- Đóng cắt một tải điện áp thấp bên ngoài bằng relay, phần điều khiển cách ly quang với vi điều khiển.
- Nạp lại chương trình AT89S52 được; các IC, module cắm trên đế để dễ thay thế.

## 2.2. Sơ đồ khối

```text
 Adapter 12 V ─► J1/J7 ─► D2 SR360 ─► +12V ─┬─► LM7805 ─► +5V ─┬─► AT89S52, DHT11, nút nhấn
                                           │                  ├─► TXS0108E phía B (5 V)
                                           │                  └─► ESP32-C3 (chân 5V) ─► 3V3 ─► OLED, TXS phía A
                                           └─► Cuộn relay K1, Q1, phototransistor PC817

 DHT11 ──1 dây──► AT89S52 ◄── SW1 (đổi trang)
                    │ P0.3/P0.4 (I²C 5 V)    ┌──► OLED SSD1315 (I²C 3,3 V)
                    ├──────────────► TXS0108E ┤
                    │ P3.0/P3.1 (UART 5 V)   └──► ESP32-C3 UART1 ──Wi-Fi──► ThingsBoard
                    │                              GPIO0 ──► OE của TXS0108E
                    └── P2.0 ──► PC817 ──► Q1 ──► Relay K1 ──► J6 (tải ngoài)
```

*Hình 2.1. Sơ đồ khối hệ thống (sẽ vẽ lại dạng hình trong bản Word).*

Các khối chính:

- **Khối nguồn:** biến 12 V thành 5 V; cấp 12 V riêng cho phía relay.
- **Khối xử lý trung tâm AT89S52:** đọc cảm biến, hiển thị, điều khiển relay và truyền dữ liệu.
- **Khối hiển thị và giao diện:** OLED, nút đổi trang, nút reset.
- **Khối chuyển mức logic TXS0108E:** nối các đường tín hiệu 5 V với các đường 3,3 V.
- **Khối kết nối mạng ESP32-C3:** Wi-Fi, NTP, gửi dữ liệu lên nền tảng IoT.
- **Khối relay cách ly quang:** đóng cắt tải ngoài theo nhiệt độ.

## 2.3. Thiết kế khối nguồn

### 2.3.1. Sơ đồ và nguyên lý

- **Đầu vào:** nguồn 12 V cấp qua jack DC J1 (5,5 × 2,1 mm, tâm dương) hoặc cầu đấu 2 chân J7. Hai đầu vào mắc song song, chỉ dùng một trong hai.
- **Chống ngược cực:** diode Schottky D2 (SR360, 3 A, 60 V) mắc nối tiếp ở đầu vào. Nếu cắm ngược cực, D2 không dẫn nên mạch không nhận điện áp âm. Điện áp sau D2 là đường **+12V**, giảm khoảng 0,5 V so với adapter.
- **Ổn áp 5 V:** đường +12V cấp cho LM7805 (U7) để tạo đường **+5V**. Tụ hóa C14 (100 µF, ≥ 25 V) lọc ở đầu vào; tụ gốm C16 (100 nF) đặt sát chân ra.
- **Nguồn 3,3 V:** lấy từ bộ ổn áp có sẵn trên bo ESP32-C3 SuperMini (chân 3V3). Nguồn này cấp cho OLED và phía A của TXS0108E.
- **Phía relay:** cuộn relay, phototransistor của PC817 và transistor Q1 lấy nguồn trực tiếp từ +12V. Như vậy dòng cuộn relay không đi qua LM7805 và không gây sụt áp trên đường 5 V.
- **Điểm đo kiểm:** ba điểm đo TP1, TP2, TP3 tương ứng +5V, +3V3 và GND.

### 2.3.2. Tính toán tỏa nhiệt LM7805

Dòng tiêu thụ trên đường 5 V ước tính khoảng 180 mA khi hoạt động bình thường, gồm ESP32-C3 khi có Wi-Fi, AT89S52 và OLED. Dòng có thể lên khoảng 450 mA trong các xung phát Wi-Fi. Đây là giá trị ước tính, chưa đo trên mạch thật.

Công suất tỏa nhiệt trên LM7805:

- P = (V_IN − V_OUT) × I ≈ (12 − 0,5 − 5) × 0,18 ≈ 1,2 W khi hoạt động bình thường.
- P có thể lên gần 2,5 W ở dòng đỉnh.

Vì vậy LM7805 được đặt nằm ngang, vít tab xuống mạch in. Tab của LM7805 nối GND nên có thể bắt trực tiếp xuống vùng đồng GND, không cần đệm cách điện. Mạch in phủ đồng GND ở cả hai mặt; hai mặt nối với nhau qua các chân xuyên lỗ nối GND. Nếu khi thử nghiệm thấy LM7805 quá nóng, có thể gắn thêm tản nhôm hoặc dùng adapter 9 V.

## 2.4. Khối vi điều khiển AT89S52

- **Nguồn:** chân 40 (VCC) nối +5V, chân 20 nối GND; tụ C1 100 nF đặt cạnh chân 40, cực còn lại nối vùng đồng GND.
- **Dao động:** thạch anh Y1 11,0592 MHz nối giữa XTAL1 (chân 19) và XTAL2 (chân 18). Tụ C9 và C10 22 pF nối từ mỗi đầu thạch anh xuống GND.
- **Reset:** AT89S52 reset ở mức cao. Mạch reset gồm C2 10 µF từ +5V xuống chân RST (chân 9) và R1 10 kΩ từ RST xuống GND.
  - Khi cấp nguồn, C2 nạp điện qua R1 nên giữ RST ở mức cao trong khoảng thời gian cỡ R1·C2 ≈ 100 ms rồi giảm dần về mức thấp. Như vậy chip được reset tự động khi bật nguồn.
  - Nút SW2 nối RST lên +5V để reset bằng tay.
- **Chế độ chạy:** chân EA (chân 31) nối +5V để chạy chương trình trong Flash nội. PSEN (chân 29) và ALE (chân 30) để hở.
- **Cổng nạp ISP J3:** gồm 6 chân RST, VCC, GND, MISO (P1.6), SCK (P1.7) và MOSI (P1.5), dùng cho mạch nạp Burn-E. Cách nạp chính là tháo chip ra để nạp ngoài mạch, nên AT89S52 được lắp trên đế DIP-40 (SK1).

**Bảng 2.1. Phân bổ chân AT89S52**

| Chân | Tên | Chức năng | Nối tới |
|---|---|---|---|
| 6, 7, 8 | P1.5, P1.6, P1.7 | MOSI, MISO, SCK | J3 (ISP) |
| 9 | RST | Reset | C2, R1, SW2, J3 |
| 10 | P3.0/RXD | Nhận UART | TXS0108E B2 |
| 11 | P3.1/TXD | Phát UART | TXS0108E B1 |
| 12 | P3.2 | Dữ liệu DHT11 | U5 chân 2, R2 kéo lên |
| 13 | P3.3 | Nút đổi trang | SW1, R3 kéo lên |
| 18, 19 | XTAL2, XTAL1 | Dao động | Y1, C9, C10 |
| 21 | P2.0 | Điều khiển relay | Cathode LED PC817 |
| 35 | P0.4 | SCL I²C (phần mềm) | TXS0108E B7, R9 kéo lên |
| 36 | P0.3 | SDA I²C (phần mềm) | TXS0108E B8, R8 kéo lên |
| 31 | EA | Chạy Flash nội | +5V |
| 20, 40 | GND, VCC | Nguồn | GND, +5V |

## 2.5. Khối cảm biến và nút nhấn

- **DHT11 (U5, loại 4 chân):**
  - Chân 1 nối +5V, chân 2 (DATA) nối P3.2, chân 3 để trống, chân 4 nối GND.
  - Điện trở R2 4,7 kΩ kéo đường DATA lên +5V.
  - Cảm biến nên đặt xa LM7805 và ESP32 để không bị nhiệt của hai linh kiện này làm sai số đo.
- **Nút đổi trang SW1:** nối P3.3 xuống GND. R3 10 kΩ kéo chân lên +5V, nên khi nhấn nút chân đọc mức thấp. Chống dội phím được xử lý trong phần mềm.

## 2.6. Khối hiển thị OLED

- Module OLED 0,96 inch cắm vào đế J4 (1×4 chân, bước 2,54 mm), thứ tự chân GND, VCC, SCL, SDA.
- Module cấp nguồn **3,3 V**. Hai đường SCL, SDA đi qua kênh A7 và A8 của TXS0108E để nối với P0.4 (chân 35) và P0.3 (chân 36) của AT89S52.
- Địa chỉ I²C mặc định là 0x3C. Nếu module dùng 0x3D thì đổi hằng `OLED_ADDR` trong firmware.
- Footprint của J4 có vẽ đường viền thật của module, khoảng 27,3 × 27,8 mm, kèm 4 lỗ M2 để bắt cọc đỡ. Nhờ vậy khi bố trí mạch in thấy được phần diện tích module chiếm.

## 2.7. Khối chuyển mức logic TXS0108E và ESP32-C3

TXS0108E dùng dạng module cắm vào hai hàng đế 1×10 chân.

- **Nguồn:** VCCB nối +5V, VCCA nối +3V3 từ ESP32, GND chung.
- **Chân OE:**
  - Nối GPIO0 của ESP32-C3. Điện trở R4 100 kΩ kéo OE xuống GND.
  - Khi ESP32 đang khởi động, OE ở mức thấp nên mọi kênh ở trạng thái trở kháng cao.
  - Sau khoảng 100 ms, khi nguồn hai phía đã ổn định, firmware ESP32 mới đưa OE lên mức cao để bật các kênh.
- **Điện trở kéo lên I²C:** cổng P0 của AT89S52 là cực máng hở và không có điện trở kéo lên nội, nên phía 5 V có R8, R9 (10 kΩ) kéo SDA, SCL lên +5V. Phía 3,3 V dùng điện trở kéo lên nội của TXS0108E và điện trở có sẵn trên module OLED.
- Cần kiểm tra module TXS0108E mua về: nếu có điện trở hoặc cầu nối kéo cứng OE lên nguồn thì phải tháo ra.

**Bảng 2.2. Phân kênh TXS0108E**

| Kênh | Phía A (3,3 V) | Phía B (5 V) | Tín hiệu |
|---|---|---|---|
| A1/B1 | ESP32 GPIO3 (RX UART1) | AT89S52 P3.1 (TXD) | AT89S52 → ESP32 |
| A2/B2 | ESP32 GPIO4 (TX UART1) | AT89S52 P3.0 (RXD) | ESP32 → AT89S52 |
| A7/B7 | OLED SCL | AT89S52 P0.4 | Xung nhịp I²C |
| A8/B8 | OLED SDA | AT89S52 P0.3 | Dữ liệu I²C |
| OE | ESP32 GPIO0, R4 xuống GND | — | Bật/tắt bộ chuyển mức |
| A3–A6, B3–B6 | Để trống | Để trống | — |

Các kênh và chân được chọn theo vị trí linh kiện trên mạch in. Kênh B1, B2 nằm ngay phía trên chân 11, 10 (P3.1, P3.0) của AT89S52; GPIO3, GPIO4 của ESP32 được gán sao cho hai đường từ A1, A2 lên ESP32 không bắt chéo. I²C được đưa sang P0.3, P0.4 (chân 36, 35) vì hai chân này nằm ngay dưới kênh B8, B7. Kênh A7, A8 gần đế OLED. Cách chọn này giúp đường mạch ngắn và ít bắt chéo. UART không chuyển sang P0 được vì bộ UART phần cứng của AT89S52 chỉ ra ở P3.0, P3.1.

**ESP32-C3 SuperMini (U2)** cắm trên hai hàng đế 1×8 chân, lấy nguồn từ +5V qua chân 5V. Không cắm cáp USB vào ESP32 khi mạch đang cấp nguồn 12 V, để tránh cấp ngược nguồn giữa USB và LM7805.

## 2.8. Khối relay cách ly quang

**Bảng 2.3. Linh kiện khối relay**

| Phía | Linh kiện | Kết nối |
|---|---|---|
| 5 V | R6 2,2 kΩ | +5V → anode LED PC817 (chân 1) |
| 5 V | U8 PC817 chân 2 | Cathode LED → P2.0 AT89S52 |
| 12 V | U8 chân 4, chân 3 | Collector → +12V; emitter → R5 |
| 12 V | R5 4,7 kΩ; R7 10 kΩ | Emitter PC817 → R5 → base Q1; R7 từ base xuống GND |
| 12 V | Q1 2SC1815-GR | Emitter → GND; collector → cuộn K1 |
| 12 V | K1 SRD-12VDC-SL-C | Cuộn giữa +12V và collector Q1 |
| 12 V | D3 1N4007 | Mắc ngược song song cuộn relay |
| Tải | J6 cầu đấu 2 chân | Chân 1 COM, chân 2 tiếp điểm NO của K1; NC để trống |

**Nguyên lý:**

- P2.0 ở **mức thấp** thì LED của PC817 sáng, phototransistor dẫn, có dòng vào base Q1, Q1 bão hòa và cuộn relay có điện.
- P2.0 ở mức cao thì relay nhả.
- Sau khi reset, các cổng của AT89S52 ở mức cao, nên relay không đóng nhầm khi vừa cấp nguồn.
- Dòng LED khoảng (5 − 1,2) / 2,2 kΩ ≈ 1,7 mA, nằm trong khả năng kéo dòng xuống của chân AT89S52.
- Cuộn relay 12 V tiêu thụ khoảng 30 mA. Dòng base của Q1 qua R5 cỡ 1–2 mA, tùy hệ số truyền dòng (CTR) của PC817, đủ để C1815 loại GR bão hòa.
- R7 giữ Q1 tắt chắc chắn khi PC817 không dẫn.

Phía LED của PC817 dùng nguồn 5 V, phía relay dùng nguồn 12 V, nhưng hai phía có chung GND. Vì vậy đây là **tách nguồn** cho cuộn relay, không phải cách ly hoàn toàn.

Tiếp điểm relay chỉ đóng cắt nguồn ngoài của tải và không nối điện với mạch. Cách đấu: (+) nguồn ngoài → J6 chân 1 (COM); J6 chân 2 (NO) → tải → (−) nguồn ngoài. Tải có điện khi relay bật, tức khi nhiệt độ ≥ 32 °C (ví dụ chạy quạt làm mát), và mất điện khi nhiệt độ giảm về ≤ 30 °C hoặc khi cảm biến lỗi. Mạch chỉ dùng cho tải điện áp thấp, không đưa điện lưới lên PCB.

## 2.9. Sơ đồ nguyên lý trên KiCad

Sơ đồ nguyên lý được vẽ trên KiCad 10 (dự án `env-monitor`).

- **Bố cục theo khối:** bản vẽ chia thành 9 khối có khung và tiêu đề: nguồn 12 V → 5 V, vi điều khiển AT89S52, nạp ISP, nút chuyển trang, cảm biến DHT11, chuyển mức TXS0108E, ESP32-C3, màn hình OLED và điều khiển relay. Trong mỗi khối, linh kiện nối bằng dây. Giữa các khối, tín hiệu nối bằng nhãn net cùng tên, ví dụ `RST`, `SDA5`, `TX51_3V3`, `DHT_DATA` và `RELAY`.

- **Ký hiệu riêng:** ESP32-C3 SuperMini và module TXS0108E được tạo thành ký hiệu và footprint riêng, mỗi module là một khối, chân ghi đúng nhãn GPIO hoặc nhãn A/B in trên module.
- **Tụ lọc:** các tụ lọc trên các module đã có sẵn trên bo module, nên mạch chính chỉ giữ 6 tụ:
  - C1: lọc nguồn AT89S52;
  - C2: mạch reset;
  - C9, C10: tụ của thạch anh;
  - C14, C16: tụ đầu vào và đầu ra LM7805.
- **Kiểm tra luật điện (ERC):** chạy bằng kicad-cli, kết quả 0 lỗi. Các chân không dùng đều được đánh dấu không kết nối.

*Hình 2.2. Sơ đồ nguyên lý toàn mạch (xuất từ KiCad, chèn khi dựng bản Word; bản đầy đủ ở Phụ lục).*

## 2.10. Thiết kế mạch in

- **Kích thước và cấu trúc:** bo mạch hai lớp, 92,5 × 84,7 mm. Linh kiện xuyên lỗ, lắp ở mặt trên; IC và module cắm trên đế.
- **Độ rộng đường mạch theo lớp net:**

  **Bảng 2.4. Lớp net và độ rộng đường mạch**

  | Lớp net | Các net | Độ rộng | Khoảng cách |
  |---|---|---|---|
  | Tín hiệu (mặc định) | Các net còn lại | 0,3–0,5 mm | 0,25 mm |
  | Power | +5V, +3V3, GND | 1,0 mm (một số nhánh ngắn 0,5 mm) | 0,3 mm |
  | Power_12V | +12V, đường jack → SR360, hai đường tải qua J6 | 2,0 mm | 0,5 mm |

- **Vùng đồng:** GND được phủ ở cả mặt trên và mặt dưới. Đường +5V đi bằng dây, không phủ đồng, để tránh nguy cơ chập giữa +5V và các chân khác khi hàn.
- **Nguyên tắc bố trí:**
  - LM7805, jack nguồn và cầu đấu 12 V đặt ở mép trên bên trái, gần nhau.
  - DHT11 đặt ở mép phải, xa LM7805.
  - ESP32 đặt ngay trên TXS0108E; AT89S52 đặt ngay dưới TXS0108E để các đường UART, I²C ngắn.
  - Khối relay và cầu đấu tải J6 gom về cạnh trái, cách xa vùng tín hiệu.
  - R8, R9 (điện trở kéo lên I²C) nằm ngang bên dưới module TXS0108E; phải hàn sát mặt bo trước khi cắm module.
  - Module OLED nằm trọn trong bo, ở góc trên bên phải.
- **Lỗ bắt vít:** một lỗ M3 ở góc phải dưới và một lỗ M2.5 ở góc trái dưới. Hai góc trên không còn chỗ do jack nguồn và module OLED.
  - Các điện trở đều nằm sát mặt bo; R1 đặt dưới header ISP, R3 đặt dọc cạnh phải module TXS0108E.
- **Đi dây:** các đường chính được đi tay; phần còn lại đi bằng công cụ tự động Freerouting, sau đó kiểm tra và sửa bằng KiCad. Đường mạch chỉ đi thẳng hoặc chéo 45°; các góc cua 90° và mẩu dây thừa sát chân linh kiện đã được vát hoặc gộp lại.
- **Kiểm tra luật thiết kế (DRC):** không còn chân chưa nối và không có lỗi điện. Còn 6 cảnh báo do R8, R9 nằm trong vùng chiếm chỗ của module TXS0108E (bố trí có chủ ý); không còn cảnh báo về chữ in lụa.
- **Trước khi đặt in:** đo khoảng cách hai hàng chân của module ESP32-C3 và TXS0108E mua về để đối chiếu footprint, sau đó xuất tệp Gerber và tệp khoan.

*Hình 2.3. Mạch in, mặt trên.*

*Hình 2.4. Mạch in nhìn nghiêng, có mô hình 3D của các module và linh kiện.*

## 2.11. Bảng vật tư và dự toán chi phí

Bảng vật tư đầy đủ gồm 42 chi tiết, xem Phụ lục. Giá tham khảo ngày 01/11/2026:

- Phần linh kiện đã có giá, tính theo lượng dùng trên một mạch: **217.140 đồng**.
- In PCB: **120.000 đồng**.

Một số linh kiện chưa khảo sát giá nên chưa tính vào tổng: J1, J6, J7, U7, D2, D3, Q1, R5, R6, U8, C14, K1. Tổng chi phí sẽ được cập nhật khi đủ giá.

## 2.12. Kết luận chương

Chương 2 đã trình bày thiết kế phần cứng gồm khối nguồn 12 V/5 V/3,3 V, khối AT89S52, khối cảm biến và hiển thị, khối chuyển mức TXS0108E cùng ESP32-C3, khối relay cách ly quang, sơ đồ nguyên lý, mạch in hai lớp đã đi dây và kiểm tra DRC, cùng dự toán chi phí. Chương 3 sẽ trình bày phần mềm điều khiển các khối phần cứng này.
