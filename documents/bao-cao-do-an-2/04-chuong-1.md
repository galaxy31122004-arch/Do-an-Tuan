# CHƯƠNG 1. TỔNG QUAN VÀ CƠ SỞ LÝ THUYẾT

## 1.1. Tổng quan hệ thống giám sát môi trường qua Internet

Hệ thống giám sát môi trường qua Internet thường gồm bốn lớp:

- **Lớp cảm biến:** đo đại lượng vật lý (nhiệt độ, độ ẩm…) và chuyển thành tín hiệu số.
- **Lớp thiết bị:** vi điều khiển thu thập, xử lý, hiển thị tại chỗ và điều khiển cơ cấu chấp hành.
- **Lớp kết nối:** module mạng (Wi-Fi) đưa dữ liệu lên Internet theo một giao thức chuẩn như HTTP hoặc MQTT.
- **Lớp ứng dụng:** nền tảng IoT lưu trữ dữ liệu theo thời gian, hiển thị dashboard, xử lý luật cảnh báo và cho phép người dùng truy cập từ trình duyệt.

Trong đề tài, AT89S52 đảm nhiệm lớp thiết bị (đo, hiển thị, điều khiển relay), ESP32-C3 đảm nhiệm lớp kết nối và ThingsBoard đảm nhiệm lớp ứng dụng. Cách chia này giúp phần đo và điều khiển tại chỗ vẫn hoạt động khi mạng gặp sự cố.

## 1.2. Vi điều khiển AT89S52

AT89S52 là vi điều khiển 8 bit họ 8051 của Atmel (nay thuộc Microchip) [1]. Các đặc điểm chính:

- Bộ nhớ chương trình Flash 8 KB, nạp được trong mạch qua giao tiếp ISP (SPI: MOSI, MISO, SCK cùng chân RST).
- RAM nội 256 byte; 32 chân vào/ra chia thành bốn cổng P0–P3.
- Ba bộ định thời/đếm 16 bit, một cổng nối tiếp UART song công và hệ thống ngắt.
- Đóng gói DIP-40; điện áp hoạt động 4,0–5,5 V.

Trong đề tài, AT89S52 dùng thạch anh 11,0592 MHz. Tần số này chia chính xác ra tốc độ baud chuẩn 9600 bit/s cho UART. Chân EA nối lên +5 V để chạy chương trình trong Flash nội. Mạch reset gồm tụ và điện trở, có thêm nút nhấn reset tay.

## 1.3. Module ESP32-C3 SuperMini

ESP32-C3 là SoC của Espressif với các đặc điểm chính:

- Lõi RISC-V 32 bit đơn nhân, tần số tối đa 160 MHz.
- Tích hợp Wi-Fi 2,4 GHz (IEEE 802.11 b/g/n) và Bluetooth LE 5.
- Ma trận GPIO cho phép gán chức năng UART lên hầu hết các chân [2].

Module ESP32-C3 SuperMini có kích thước nhỏ, gồm hai hàng 8 chân, cổng USB-C dùng để nạp và gỡ lỗi, cùng bộ ổn áp 3,3 V trên bo. ESP32-C3 làm việc ở mức logic 3,3 V nên không nối trực tiếp với các chân 5 V của AT89S52.

## 1.4. Cảm biến nhiệt độ, độ ẩm DHT11

DHT11 là cảm biến nhiệt độ, độ ẩm có ngõ ra số, giao tiếp qua **một dây dữ liệu** hai chiều. Theo datasheet, cảm biến đo nhiệt độ 0–50 °C (sai số ±2 °C) và độ ẩm tương đối 20–90 % (sai số ±5 %) [3].

Quy trình đọc một lần đo:

1. Vi điều khiển kéo đường dữ liệu xuống mức thấp tối thiểu 18 ms để đánh thức cảm biến, sau đó thả đường dây.
2. Cảm biến phản hồi bằng một xung thấp rồi một xung cao, mỗi xung khoảng 80 µs.
3. Cảm biến gửi 40 bit dữ liệu: 8 bit phần nguyên độ ẩm, 8 bit phần thập phân độ ẩm, 8 bit phần nguyên nhiệt độ, 8 bit phần thập phân nhiệt độ và 8 bit tổng kiểm tra.
4. Mỗi bit bắt đầu bằng mức thấp khoảng 50 µs. Mức cao sau đó kéo dài khoảng 26–28 µs là bit 0, khoảng 70 µs là bit 1.

Khoảng thời gian giữa hai lần đọc nên từ 1 s trở lên. Đường dữ liệu cần một điện trở kéo lên nguồn.

## 1.5. Màn hình OLED 0,96 inch SSD1315 và giao tiếp I²C

Module OLED 0,96 inch có độ phân giải 128 × 64 điểm, dùng IC điều khiển SSD1315, tương thích tập lệnh với SSD1306 [4]. OLED tự phát sáng nên không cần đèn nền, độ tương phản cao và tiêu thụ thấp khi hiển thị ít điểm sáng. Bộ nhớ hiển thị chia thành 8 trang (page), mỗi trang cao 8 điểm. Nhờ vậy mỗi trang tương ứng một dòng chữ cỡ 8 điểm, phù hợp để in 8 dòng văn bản.

**I²C** là bus nối tiếp đồng bộ hai dây:

- SDA mang dữ liệu, SCL mang xung nhịp; cả hai đường dạng cực máng hở và cần điện trở kéo lên.
- Mỗi giao dịch bắt đầu bằng điều kiện START, gửi địa chỉ 7 bit kèm bit đọc/ghi, rồi các byte dữ liệu. Mỗi byte được thiết bị nhận xác nhận bằng bit ACK, và giao dịch kết thúc bằng điều kiện STOP.
- Module OLED trong đề tài dùng địa chỉ 0x3C.

AT89S52 không có khối I²C phần cứng. Giao tiếp được thực hiện bằng phần mềm: điều khiển trực tiếp hai chân P0.3 (SDA) và P0.4 (SCL), tốc độ dưới 100 kHz.

## 1.6. Giao tiếp nối tiếp UART

UART truyền dữ liệu nối tiếp không đồng bộ qua hai đường TX và RX. Mỗi khung gồm:

- một bit start mức thấp,
- 5–9 bit dữ liệu (bit thấp truyền trước),
- bit chẵn lẻ (tùy chọn),
- một hoặc hai bit stop mức cao.

Hai bên phải thống nhất tốc độ baud và định dạng khung. Đề tài dùng định dạng 9600 bit/s, 8 bit dữ liệu, không chẵn lẻ, 1 bit stop (9600 8N1). AT89S52 dùng chân P3.1 (TXD) và P3.0 (RXD); ESP32-C3 dùng UART1 với RX tại GPIO4 và TX tại GPIO3.

## 1.7. Chuyển mức logic với TXS0108E

Phía AT89S52 làm việc ở mức 5 V, còn ESP32-C3 và OLED làm việc ở mức 3,3 V, nên cần mạch chuyển mức logic giữa hai phía. TXS0108E của Texas Instruments là bộ chuyển mức 8 kênh hai chiều, tự nhận chiều truyền, không cần chân chọn hướng [5].

- **Nguồn:** phía A cấp VCCA từ 1,2 đến 3,6 V; phía B cấp VCCB từ 1,65 đến 5,5 V; yêu cầu VCCA ≤ VCCB.
- **Kênh truyền:** mỗi kênh có điện trở kéo lên nội và mạch tăng tốc sườn. Nhờ đó dùng được cho cả đường cực máng hở (I²C) lẫn đường đẩy kéo (UART).
- **Chân OE:** OE ở mức thấp đưa mọi kênh về trạng thái trở kháng cao. Trong đề tài, OE do ESP32-C3 điều khiển và được giữ thấp bằng điện trở kéo xuống cho đến khi nguồn hai phía đã ổn định.

## 1.8. Mạch điều khiển relay cách ly quang

Relay điện từ cho phép một tín hiệu điều khiển công suất nhỏ đóng cắt một tải ở mạch điện riêng. Để tách mạch điều khiển của vi điều khiển khỏi cuộn relay, đề tài dùng opto PC817:

- Phía sơ cấp là LED hồng ngoại, phía thứ cấp là phototransistor; hai phía cách ly điện với nhau.
- Hệ số truyền dòng (CTR) cho biết tỉ lệ giữa dòng collector phía thứ cấp và dòng LED phía sơ cấp [6].

Dòng ra của phototransistor PC817 không đủ cho cuộn relay 12 V, nên cần thêm transistor NPN 2SC1815 khuếch đại dòng để đóng cuộn relay. Diode mắc song song ngược chiều với cuộn relay (diode dập) hấp thụ sức điện động tự cảm khi transistor ngắt, bảo vệ transistor.

## 1.9. Khối nguồn tuyến tính LM7805

LM7805 là IC ổn áp tuyến tính ba chân cho điện áp ra cố định 5 V, dòng ra tới 1,5 A khi được tản nhiệt đầy đủ. Điện áp vào cần cao hơn điện áp ra ít nhất khoảng 2 V [7].

Phần chênh áp giữa đầu vào và đầu ra tỏa thành nhiệt theo công thức P = (V_IN − V_OUT) × I. Vì vậy khi cấp nguồn 12 V, IC cần được tản nhiệt.

Ở đầu vào, diode Schottky SR360 (3 A, 60 V) bảo vệ mạch khi cắm ngược cực nguồn. Diode Schottky có sụt áp thuận thấp hơn diode chỉnh lưu thường. Các tụ ở đầu vào và đầu ra LM7805 giúp ổn định và lọc nhiễu nguồn.

## 1.10. Nền tảng IoT ThingsBoard và đồng bộ thời gian NTP

ThingsBoard là nền tảng IoT mã nguồn mở. Nền tảng hỗ trợ:

- thu nhận dữ liệu từ thiết bị qua HTTP, MQTT và CoAP;
- lưu dữ liệu đo theo thời gian (telemetry);
- xây dựng dashboard bằng các widget;
- xử lý luật và tạo cảnh báo (alarm) theo ngưỡng [8].

Mỗi thiết bị được cấp một mã truy cập (access token). Trong đề tài, ESP32-C3 gửi dữ liệu dạng JSON bằng phương thức HTTP POST tới API telemetry của thiết bị [9].

NTP (Network Time Protocol) cho phép thiết bị lấy thời gian chuẩn từ máy chủ thời gian qua Internet. ESP32-C3 đồng bộ giờ UTC qua NTP rồi gửi về AT89S52, nhờ đó AT89S52 hiển thị ngày giờ theo múi giờ Việt Nam (UTC+7) mà không cần module đồng hồ thời gian thực riêng.

## 1.11. Kết luận chương

Chương 1 đã trình bày mô hình hệ thống giám sát qua Internet và cơ sở lý thuyết của các linh kiện, giao thức được sử dụng. Đó là AT89S52, ESP32-C3, DHT11, OLED SSD1315 với bus I²C, UART, bộ chuyển mức TXS0108E, mạch relay cách ly quang, khối nguồn LM7805, nền tảng ThingsBoard và NTP. Chương 2 sẽ dựa trên các cơ sở này để thiết kế phần cứng của hệ thống.

---

### Tài liệu tham khảo dùng trong chương (đánh số tạm, sẽ gộp vào danh mục chung)

[1] Atmel/Microchip, *AT89S52 8-bit Microcontroller with 8K Bytes In-System Programmable Flash*, doc1919.
[2] Espressif Systems, *ESP32-C3 Series Datasheet*; *ESP-IDF Programming Guide – UART (ESP32-C3)*.
[3] Aosong, *DHT11 Humidity & Temperature Sensor Datasheet*.
[4] Solomon Systech, *SSD1315 Advance Information – 128×64 Dot Matrix OLED Driver*.
[5] Texas Instruments, *TXS0108E 8-Bit Bidirectional Voltage-Level Translator*, datasheet SCES642.
[6] Sharp, *PC817 Series Photocoupler Datasheet*.
[7] Texas Instruments, *LM78xx Series Fixed Voltage Regulators* datasheet.
[8] ThingsBoard, *ThingsBoard Community Edition Documentation*, thingsboard.io/docs.
[9] ThingsBoard, *HTTP Device API Reference*, thingsboard.io/docs/reference/http-api.
