# CHƯƠNG 3. THIẾT KẾ PHẦN MỀM

## 3.1. Tổng quan phần mềm

Phần mềm gồm ba thành phần:

- **Firmware AT89S52:**
  - Viết bằng C, biên dịch bằng SDCC; riêng đoạn đọc DHT11 viết bằng hợp ngữ vì yêu cầu thời gian chặt.
  - Chương trình chiếm khoảng 7,4 KB trong 8 KB Flash.
  - Đảm nhiệm đọc cảm biến, hiển thị OLED, điều khiển relay và gửi bản ghi đo qua UART.
- **Firmware ESP32-C3:**
  - Viết bằng Arduino framework trên PlatformIO.
  - Đảm nhiệm kết nối Wi-Fi, đồng bộ NTP, gửi dữ liệu lên ThingsBoard và báo trạng thái về AT89S52.
- **Dashboard ThingsBoard:**
  - Tệp cấu hình JSON được sinh bằng script Python, import vào nền tảng.
  - Hiển thị số đo, lịch sử, cảnh báo và trạng thái relay.

Hai vi điều khiển trao đổi với nhau bằng các khung văn bản ASCII có mã kiểm tra lỗi CRC-8. Phần định nghĩa khung dùng chung cho cả hai bên, đặt trong tệp `common/protocol.h`.

## 3.2. Giao thức truyền giữa AT89S52 và ESP32-C3

### 3.2.1. Cấu trúc khung

Thông số đường truyền UART: 9600 bit/s, 8N1. Mỗi khung có dạng:

```text
$<loại>,<trường 1>,<trường 2>,...*<CRC>\n
```

- Khung bắt đầu bằng ký tự `$` và kết thúc bằng ký tự xuống dòng.
- CRC là hai chữ số hex. Giá trị này là mã CRC-8 (đa thức 0x07, giá trị đầu 0x00, chuẩn CRC-8/SMBUS) tính trên các ký tự nằm giữa `$` và `*`.
- Bên nhận bỏ những khung sai CRC, sai định dạng hoặc có giá trị ngoài miền hợp lệ.

**Bảng 3.1. Các loại khung**

| Khung | Chiều | Nội dung | Chu kỳ |
|---|---|---|---|
| `M` | AT89S52 → ESP32 | `M,<số thứ tự>,<epoch>,<nhiệt độ×10>,<độ ẩm×10>,<cờ>` | Khoảng 2 s |
| `S` | ESP32 → AT89S52 | `S,<Wi-Fi>,<cloud>,<epoch lần gửi thành công cuối>` | 1 s |
| `T` | ESP32 → AT89S52 | `T,<epoch UTC>`, gửi 0 khi chưa đồng bộ giờ | Khoảng 1 s |

Byte cờ trong khung M có ba bit có nghĩa. Vì vậy bên nhận chỉ chấp nhận giá trị cờ trong khoảng 0–7.

- Bit 0: số đo cảm biến hợp lệ.
- Bit 1: thời gian UTC hợp lệ.
- Bit 2: relay đang bật.

Nhiệt độ và độ ẩm truyền dạng số nguyên gấp 10 lần giá trị thật, để không phải xử lý số thực trên AT89S52. Ví dụ, khung `$M,125,1762581005,315,650,5*xx` cho biết: bản ghi thứ 125, nhiệt độ 31,5 °C, độ ẩm 65,0 %, cảm biến hợp lệ và relay đang bật.

### 3.2.2. Xử lý lỗi đường truyền

- **AT89S52:**
  - Nhận khung bằng ngắt nối tiếp, ghi vào bộ đệm 48 byte.
  - Khung bị cắt ngang hoặc sai CRC thì bỏ qua.
  - Nếu quá khoảng 6 s không nhận được khung S hợp lệ, AT89S52 coi Wi-Fi và cloud là mất kết nối và hiển thị trạng thái tương ứng.
- **ESP32:**
  - Nhận khung trong một tác vụ FreeRTOS riêng. Vì vậy các khung UART vẫn được đọc liên tục trong lúc vòng lặp chính bị chặn bởi kết nối HTTPS.
  - Đếm số khung lỗi và in ra cổng Serial để chẩn đoán.

## 3.3. Firmware AT89S52

### 3.3.1. Cấu hình phần cứng

- **Timer 1:** chế độ tự nạp lại 8 bit, TH1 = 0xFD, tạo tốc độ baud 9600 với thạch anh 11,0592 MHz.
- **Cổng nối tiếp:** chế độ 1 (SCON = 0x50), bật ngắt nối tiếp.
- **Timer 0:** chế độ 16 bit, dùng để tạo trễ và đo độ rộng xung khi đọc DHT11. Mỗi nhịp của Timer 0 bằng 12 / 11,0592 MHz ≈ 1,085 µs.
- **Khởi động:** ngay khi khởi động, P1, P2, P3 được đặt mức cao. Nhờ đó P2.0 ở mức cao và relay tắt.

### 3.3.2. Vòng lặp chính

Chương trình chạy một vòng lặp vô hạn, mỗi vòng có trễ 10 ms. Biến `tick` đếm từ 0 đến 199, tức một chu kỳ khoảng 2 s. Mỗi vòng thực hiện:

1. Xử lý khung điều khiển đã nhận (S hoặc T) nếu có: cập nhật trạng thái Wi-Fi/cloud hoặc đồng bộ đồng hồ.
2. Cập nhật đồng hồ phần mềm đã đồng bộ từ khung T.
3. Đọc nút đổi trang và chống dội: nút phải được giữ liên tục khoảng 50 ms (5 vòng) mới được tính là một lần nhấn. Mỗi lần nhấn chuyển giữa trang 0 và trang 1.
4. Khi `tick = 0` (khoảng 2 s một lần):
   - đọc DHT11;
   - cập nhật relay;
   - tăng số thứ tự bản ghi;
   - gửi khung M.
5. Vẽ lại màn hình khi có thay đổi.

*Hình 3.1. Lưu đồ vòng lặp chính firmware AT89S52 (vẽ khi dựng bản Word).*

### 3.3.3. Đọc cảm biến DHT11

1. AT89S52 kéo chân P3.2 xuống mức thấp trong 18 ms rồi thả ra.
2. Chương trình bắt 40 bit dữ liệu bằng một đoạn hợp ngữ. Trong lúc đọc, ngắt nối tiếp bị tắt để không làm lệch thời gian đo xung.
3. Với mỗi bit, Timer 0 đo độ rộng mức cao:
   - lớn hơn 40 nhịp (khoảng 43 µs) là bit 1, ngược lại là bit 0;
   - nếu quá 110 nhịp (khoảng 119 µs) không có sườn xung thì báo lỗi.
4. Sau khi nhận đủ 5 byte, chương trình kiểm tra tổng kiểm tra. Nếu sai, lần đọc đó bị coi là lỗi.

### 3.3.4. Điều khiển relay có trễ

Relay được điều khiển theo nhiệt độ với vùng trễ (hysteresis) 2 °C. Vùng trễ tránh cho relay đóng cắt liên tục khi nhiệt độ dao động quanh một ngưỡng.

- Nhiệt độ ≥ 32,0 °C thì bật relay.
- Nhiệt độ ≤ 30,0 °C thì tắt relay.
- Trong khoảng giữa hai ngưỡng thì giữ nguyên trạng thái cũ.
- Nếu đọc DHT11 lỗi, relay tắt để an toàn.

Hai ngưỡng khai báo bằng hằng `RELAY_ON_T10` và `RELAY_OFF_T10` trong tệp `board.h`. Trạng thái relay được gửi lên cloud qua bit 2 của byte cờ trong khung M.

### 3.3.5. Giao tiếp I²C và hiển thị OLED

- **I²C bằng phần mềm:** các hàm START, STOP và ghi byte điều khiển trực tiếp chân P1.0 và P1.1.
  - Khi thả đường SCL, chương trình chờ SCL thực sự lên mức cao trước khi tiếp tục, vì thiết bị nhận có thể giữ SCL ở mức thấp để làm chậm bus (clock stretching).
  - Mỗi byte gửi đi được kiểm tra bit ACK.
- **Hiển thị chữ:** bảng font 5 × 7 điểm lưu trong bộ nhớ chương trình. Mỗi dòng chữ tương ứng một trang 8 điểm của SSD1315, nên màn hình có 8 dòng, mỗi dòng tối đa khoảng 21 ký tự.
- **Khởi tạo lại OLED:** ESP32 bật chân OE của TXS0108E chậm hơn AT89S52 khoảng 100 ms. Vì vậy nếu lần khởi tạo OLED đầu tiên thất bại, chương trình thử khởi tạo lại ở các lần vẽ màn hình sau.

**Bảng 3.2. Nội dung hai trang OLED**

| Dòng | Trang 0 – Môi trường | Trang 1 – Mạng |
|---|---|---|
| 0 | ENVIRONMENT MONITOR | NETWORK STATUS |
| 2 | TEMP: xx.x C (hoặc SENSOR ERROR) | WIFI: CONNECTED / OFFLINE |
| 4 | HUM: xxx.x % (hoặc CHECK DHT11) | CLOUD: HTTP OK / WAIT / ERROR |
| 5 | RELAY: ON / OFF | — |
| 6 | Ngày giờ UTC+7 hoặc TIME NOT SYNCED | LAST SEND: hh:mm:ss hoặc NONE |
| 7 | BTN: CHANGE PAGE | BTN: CHANGE PAGE |

### 3.3.6. Đồng hồ hiển thị

- AT89S52 không có module đồng hồ thời gian thực. Khi nhận khung T hợp lệ, chương trình lưu giá trị epoch UTC và tự đếm tăng theo nhịp vòng lặp.
- Khi hiển thị, epoch được cộng 25 200 s (7 giờ) rồi đổi sang ngày, tháng, năm, giờ, phút, giây. Phép đổi hỗ trợ các năm từ 2000 đến 2099.
- Nếu chưa nhận được giờ hợp lệ, màn hình hiện "TIME NOT SYNCED".

## 3.4. Firmware ESP32-C3

### 3.4.1. Khởi động

1. Đặt GPIO0 (chân OE của TXS0108E) ở mức thấp, rồi khởi tạo UART1 với tốc độ 9600 bit/s, RX = GPIO4, TX = GPIO3.
2. Chờ 100 ms cho nguồn ổn định, sau đó đưa OE lên mức cao để bật bộ chuyển mức.
3. Kết nối Wi-Fi ở chế độ station và bật tự kết nối lại.
4. Cấu hình NTP với máy chủ `pool.ntp.org` và `time.google.com`.
5. Tạo tác vụ FreeRTOS `host-uart` để xử lý UART.

Thông tin Wi-Fi, địa chỉ máy chủ, mã truy cập thiết bị (token) và chứng chỉ CA được khai báo trong tệp `secrets.h`. Tệp này không đưa lên kho mã nguồn. Nếu cấu hình còn để giá trị mẫu, firmware không kết nối mạng.

### 3.4.2. Tác vụ UART

- Ghép các ký tự nhận được thành khung, kiểm tra CRC và phân tích khung M.
- Khi khung M hợp lệ, ghi bản ghi vào hàng đợi một phần tử. Bản ghi mới ghi đè bản ghi cũ, nên hàng đợi luôn giữ số đo mới nhất.
- Gắn dấu thời gian UTC tại thời điểm nhận khung nếu ESP32 đã đồng bộ NTP.
- Mỗi giây gửi khung S chứa trạng thái Wi-Fi, trạng thái cloud và thời điểm gửi thành công gần nhất. Trạng thái cloud chỉ báo "OK" nếu lần gửi thành công gần nhất cách đó không quá 30 s.
- Gửi khung T chứa giờ UTC hiện tại, xen giữa hai khung S.

### 3.4.3. Gửi dữ liệu lên ThingsBoard

Vòng lặp chính gửi dữ liệu mỗi 10 s nếu thỏa đủ các điều kiện sau:

- đã kết nối Wi-Fi;
- đã đồng bộ giờ;
- có bản ghi mới, nhận cách đó không quá 6 s.

Dữ liệu gửi bằng HTTPS POST tới địa chỉ `/api/v1/<token>/telemetry`, có kiểm tra chứng chỉ máy chủ. Ví dụ nội dung gửi:

```json
{"ts":1762581005000,"values":{"temperature":31.5,"humidity":65.0,"sensor_ok":true,
 "time_ok":true,"relay":true,"sequence":125,"rssi":-58,"demo":false}}
```

*Ví dụ minh họa định dạng, không phải số đo thật.*

- Khi cảm biến lỗi, ESP32 không gửi trường nhiệt độ và độ ẩm, chỉ gửi `sensor_ok: false`. Nhờ vậy nền tảng không lưu giá trị 0 giả.
- Gửi thất bại thì bỏ qua bản ghi đó, không lưu bù. Khi mất Wi-Fi, ESP32 thử kết nối lại mỗi 15 s.
- Chế độ `DEMO_MODE` sinh dữ liệu giả để thử dashboard khi chưa có mạch. Mọi bản ghi gửi ở chế độ này có cờ `demo: true` để phân biệt với số đo thật.

*Hình 3.2. Lưu đồ firmware ESP32-C3 (vẽ khi dựng bản Word).*

## 3.5. Dashboard ThingsBoard

Dashboard `environment-monitor.json` được sinh bằng script `dashboard/generate.py` từ các widget chuẩn của ThingsBoard và gồm 12 widget:

- **Thẻ số đo:**
  - nhiệt độ, độ ẩm;
  - trạng thái thiết bị trực tuyến;
  - cảm biến hợp lệ, đồng bộ thời gian;
  - chế độ mô phỏng;
  - trạng thái relay (quạt).
- **Biểu đồ lịch sử** nhiệt độ và độ ẩm: chọn được khoảng thời gian; vẽ dạng điểm để thấy rõ các khoảng mất dữ liệu.
- **Bảng lịch sử bản ghi:** xuất được tệp CSV.
- **Biểu mẫu ngưỡng cảnh báo:** nhập bốn ngưỡng nhiệt độ thấp/cao và độ ẩm thấp/cao, lưu dưới dạng thuộc tính phía máy chủ (server attribute) của thiết bị.
- **Bảng lịch sử cảnh báo.**

Luật cảnh báo cấu hình trong hồ sơ thiết bị (device profile). Cảnh báo được tạo khi `sensor_ok = true` và giá trị vượt ngưỡng, và được xóa khi giá trị trở lại trong ngưỡng. Các ngưỡng này chỉ dùng trên nền tảng, không gửi xuống AT89S52.

*Hình 3.3. Giao diện dashboard (chèn ảnh chụp khi chạy với dữ liệu thật).*

## 3.6. Kiểm thử phần mềm

Các kiểm thử phần mềm đã có trong thư mục `tests/`:

- `test_protocol.c`: kiểm tra hàm CRC, phân tích khung và chuyển đổi ngày giờ trên máy tính.
- `test_at89s52_sim.py`: chạy mã máy 8051 đã biên dịch trên trình mô phỏng uCsim. Kịch bản kiểm tra việc đọc xung DHT11 (26 µs và 70 µs), hiển thị và xử lý khung điều khiển, không cần phần cứng.
- `check_artifacts.py`: kiểm tra cấu trúc dashboard, danh sách linh kiện và tổng kiểm tra (checksum) của tệp HEX AT89S52. Lần chạy gần nhất đạt yêu cầu.

Đây là kiểm thử phần mềm, không thay thế kiểm thử trên mạch thật ở Chương 4.

## 3.7. Kết luận chương

Chương 3 đã trình bày giao thức khung có CRC giữa hai vi điều khiển, firmware AT89S52, firmware ESP32-C3 và dashboard ThingsBoard.

- Firmware AT89S52 đảm nhiệm đo, hiển thị hai trang và điều khiển relay có trễ.
- Firmware ESP32-C3 đảm nhiệm Wi-Fi, NTP và gửi dữ liệu qua HTTPS.
- Dashboard cung cấp số đo, lịch sử, xuất CSV và cảnh báo.
- Phần đo, hiển thị và điều khiển relay tại chỗ vẫn chạy độc lập khi mất kết nối mạng.
