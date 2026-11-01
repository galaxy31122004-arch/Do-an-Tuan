# Build, cấu hình và kiểm thử firmware

## Phần cứng mặc định

PIC16F877A DIP-40 / 20 MHz / 5 V; DHT11 tại RB0; nút trang RB1; MSSP I²C RC3/RC4; UART RC6/RC7, 9600 8N1. ESP32-C3 SuperMini nhận tại GPIO4, phát tại GPIO5, GPIO6 điều khiển OE module TXS0108E. Xem `hardware/wiring.md` trước khi cấp nguồn.

## ESP32 — PlatformIO

Đích hiện tại là ESP32-C3 SuperMini 4 MB: dùng cấu hình chip `esp32-c3-devkitm-1` với USB CDC làm console. UART1 nối PIC tại RX=GPIO4, TX=GPIO5; OE=GPIO6. Không dùng Serial2 hoặc sơ đồ chân WROOM cũ. Nếu lần đầu chưa thấy cổng USB để nạp, giữ BOOT, nhấn/thả RESET rồi thả BOOT để vào download mode theo board thực tế. Chừa GPIO18/19 cho USB; không dùng chân strap GPIO2/8/9 cho UART/OE trong thiết kế này.

```powershell
Copy-Item firmware/esp32/include/secrets.example.h firmware/esp32/include/secrets.h
# Điền Wi-Fi, HTTPS origin, device token và CA trong secrets.h.
pio run -d firmware/esp32 -e esp32c3
pio run -d firmware/esp32 -e esp32c3 -t upload --upload-port COM6
pio device monitor -b 115200 --port COM6
```

Thay COM6 bằng cổng thực tế; lệnh upload chỉ chạy khi người dùng đã nối đúng board. Environment `demo` tạo số liệu giả, đánh dấu telemetry `demo=true`; không cần PIC cho bài thử cloud. Bản live luôn phát `demo=false`.

Firmware gửi tối đa một bản ghi mới mỗi 10 giây; chờ frame PIC mới sau khi Wi-Fi kết nối lại. HTTPS có timeout, UART chạy task riêng và queue chỉ chứa một bản mới nhất. Lỗi gửi không tạo backlog. ESP32 lấy giờ NTP và gửi UTC cho PIC khoảng mỗi giây; khi chưa đồng bộ thì gửi 0 để PIC báo TIME NOT SYNCED. PIC chỉ giữ bản giờ hiển thị, đánh dấu hết hạn sau 600 vòng lặp không nhận cập nhật (khoảng vài giây). Khi mất Internet nhưng còn nguồn, ESP32 vẫn duy trì giờ đã đồng bộ và tiếp tục gửi cho PIC. Mất điện rồi bật lại cần NTP; không có pin giữ giờ. ESP32 gắn timestamp UTC lúc nhận frame đo từ PIC. Bộ ESP32 Arduino hiện dùng time_t 32-bit, vì vậy cần nâng toolchain trước mốc năm 2038.

## PIC — nạp HEX bằng Burn-E

Theo lựa chọn của người dùng, bỏ bước cài/build compiler trên máy này; quy trình thao tác tập trung vào Burn-E. Burn-E nạp HEX, không biên dịch C. Mã `main.c` hiện viết theo cú pháp XC8 (`xc.h`); cần có file HEX được biên dịch từ đúng mã nguồn và kiểm tra bộ nhớ trước khi nạp. Workspace chưa có HEX PIC đã kiểm chứng, không dùng HEX của mạch khác.

1. Mở phần mềm đi kèm đúng phiên bản Burn-E và xác nhận phần mềm nhận mạch nạp.
2. Tắt nguồn PCB, tháo PIC khỏi SK1; đặt PIC16F877A DIP-40 vào vị trí đế/adapter được Burn-E hướng dẫn. Không suy đoán vị trí chân 1 hoặc đầu cáp.
3. Chọn đúng PIC16F877A, mở HEX và kiểm tra config: HS, Y1 20 MHz, LVP OFF, watchdog OFF theo firmware. Không ghi đè tùy tiện config bits.
4. Nạp theo trình tự phần mềm cung cấp rồi chạy Verify; kiểm tra kết quả thành công trước khi tháo chip.
5. Tắt nguồn/nhả đế theo hướng dẫn Burn-E, lấy PIC ra, cắm lại SK1 đúng chiều khi PCB chưa cấp điện. Cấp nguồn và kiểm tra đo/hiển thị/UART.

J3 là header ICSP dự phòng, không bắt buộc cho cách nạp ngoài mạch. Chỉ dùng khi bản Burn-E hỗ trợ và đã đối chiếu pinout cáp, nguồn và VPP. Không coi Burn-E là bộ debug trong MPLAB.

Driver OLED dùng font chữ hoa 5×7 và truyền từng dòng, không cần framebuffer 1.024 byte. Hiển thị hai trang qua nút nhấn chống dội; thông báo mạng trên PIC hết hạn nếu không nhận trạng thái ESP32. `LAST SEND` là thời gian ESP32 nhận HTTP 2xx, không khẳng định mọi widget đã cập nhật. OLED dùng địa chỉ 0x3C; chỉnh `board.h` nếu module là 0x3D. Bộ lệnh khởi tạo cần kiểm tra trên SSD1315 thực tế; không coi build là bằng chứng màn hình đã hoạt động.

PIC vẫn đo khi Internet mất. Mọi chờ DHT/I²C có giới hạn; lỗi cảm biến không trở thành số đo 0 hợp lệ. Việc mất nguồn PIC/ESP32 hoặc bus I²C bị chập cần thử trực tiếp trong nghiệm thu; đây chưa phải hệ thống công nghiệp tự phục hồi đã kiểm định.

## Giao thức UART

ASCII, kết thúc LF, payload có CRC-8/SMBUS viết hai ký tự hex (polynomial 0x07, init 0, không reflect, xorout 0). Không đưa khoảng trắng vào frame.

```text
$M,sequence,epochUTC,temperature10,humidity10,flags*XX\n
$S,wifiOK,cloudOK,lastSuccessEpochUTC*XX\n
$T,epochUTC*XX\n
```

Checksum tính trên phần giữa `$` và `*`, không gồm hai dấu đó. Nhiệt độ/độ ẩm theo đơn vị 0,1; flags bit0 = sensor valid, bit1 = time valid. Khi sensor lỗi flags bit0=0, ESP32 không gửi hai khóa temperature/humidity. Khi nhận frame, ESP32 gắn thời gian của nó nếu đã đồng bộ và cập nhật bit1; PIC dùng giờ phản chiếu từ frame T cho OLED. T=0 hoặc cập nhật quá hạn sẽ xóa trạng thái giờ hợp lệ. Cloud dùng UTC; OLED cộng UTC+7.

Payload HTTP: `{"ts":<epoch_ms>,"values":{"temperature":25.3,"humidity":64.1,"sensor_ok":true,"time_ok":true,"sequence":42,"rssi":-60,"demo":false}}`. Device ID do token xác định, không cần phát token trong payload/log.

## Kiểm tra trên máy

```powershell
# Với C compiler sẵn có:
cc tests/test_protocol.c -o tests/protocol-test
# Trên máy hiện tại có Zig trong .tools:
.tools/ziglang/zig.exe cc tests/test_protocol.c -o tests/protocol-test.exe
tests/protocol-test.exe
python tests/check_artifacts.py
```

Các kiểm tra này không thay thế đo timing DHT, xác nhận bộ nhớ/HEX PIC bằng compiler phù hợp, kiểm tra điện áp hoặc import dashboard vào deployment thực tế. Việc bỏ bước cài/compiler không biến mã C thành file nạp được.
