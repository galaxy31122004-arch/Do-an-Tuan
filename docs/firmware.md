# Build, cấu hình và kiểm thử firmware

## Phần cứng mặc định

PIC16F877A DIP-40 / 20 MHz / 5 V; DHT11 tại RB0; nút trang RB1; MSSP I²C RC3/RC4; UART RC6/RC7, 9600 8N1. ESP32-WROOM-32 DevKit nhận tại GPIO16 và phát tại GPIO17. Xem `hardware/wiring.md` trước khi cấp nguồn.

## ESP32 — PlatformIO

```powershell
Copy-Item firmware/esp32/include/secrets.example.h firmware/esp32/include/secrets.h
# Điền Wi-Fi, HTTPS origin, device token và CA trong secrets.h.
pio run -d firmware/esp32 -e esp32dev
pio run -d firmware/esp32 -e esp32dev -t upload --upload-port COM6
pio device monitor -b 115200 --port COM6
```

Thay COM6 bằng cổng thực tế; lệnh upload chỉ chạy khi người dùng đã nối đúng board. Environment `demo` tạo số liệu giả, đánh dấu telemetry `demo=true`; không cần PIC cho bài thử cloud. Bản live luôn phát `demo=false`.

Firmware gửi tối đa một bản ghi mới mỗi 10 giây; chờ frame PIC mới sau khi Wi-Fi kết nối lại. HTTPS có timeout, UART chạy task riêng và queue chỉ chứa một bản mới nhất. Lỗi gửi không tạo backlog. Khi NTP hợp lệ, ESP32 gửi thời gian UTC để PIC ghi DS1307; thử lại mỗi 10 giây nếu RTC chưa hợp lệ, sau đó đồng bộ định kỳ một giờ. Bộ ESP32 Arduino hiện dùng time_t 32-bit, vì vậy cần nâng toolchain trước mốc năm 2038.

## PIC — MPLAB X / XC8

1. Cài MPLAB X, XC8 và device pack có PIC16F877A. Tạo Standalone Project, chọn đúng chip và programmer.
2. Thêm `firmware/pic/main.c`; giữ nguyên `board.h` và `../common/protocol.h` theo cây thư mục.
3. Clock cấu hình HS với Y1 20 MHz. Firmware đã chứa config bits, không bật LVP hoặc watchdog ngoài ý muốn.
4. Build bằng IDE hoặc chạy `firmware/pic/build.ps1 -Compiler 'đường-dẫn/xc8-cc.exe'`. Kiểm tra memory summary phải vừa **368 byte RAM và 8K program words**, đồng thời xem cảnh báo stack/call depth; chưa xác nhận được các mục này khi chưa có XC8.
5. Nạp file HEX do XC8 sinh ra qua ICSP J3; kiểm tra oscillator, I²C, UART trên mạch thật.

Driver OLED dùng font chữ hoa 5×7 và truyền từng dòng, không cần framebuffer 1.024 byte. Hiển thị hai trang qua nút nhấn chống dội; thông báo mạng trên PIC hết hạn nếu không nhận trạng thái ESP32. `LAST SEND` là thời gian ESP32 nhận HTTP 2xx, không khẳng định mọi widget đã cập nhật. OLED dùng địa chỉ 0x3C; chỉnh `board.h` nếu module là 0x3D. Bộ lệnh khởi tạo cần kiểm tra trên SSD1315 thực tế; không coi build là bằng chứng màn hình đã hoạt động.

PIC vẫn đo khi Internet mất. Mọi chờ DHT/I²C có giới hạn; lỗi cảm biến không trở thành số đo 0 hợp lệ. Việc mất nguồn PIC/ESP32 hoặc bus I²C bị chập cần thử trực tiếp trong nghiệm thu; đây chưa phải hệ thống công nghiệp tự phục hồi đã kiểm định.

## Giao thức UART

ASCII, kết thúc LF, payload có CRC-8/SMBUS viết hai ký tự hex (polynomial 0x07, init 0, không reflect, xorout 0). Không đưa khoảng trắng vào frame.

```text
$M,sequence,epochUTC,temperature10,humidity10,flags*XX\n
$S,wifiOK,cloudOK,lastSuccessEpochUTC*XX\n
$T,epochUTC*XX\n
```

Checksum tính trên phần giữa `$` và `*`, không gồm hai dấu đó. Nhiệt độ/độ ẩm theo đơn vị 0,1; flags bit0 = sensor valid, bit1 = RTC valid. Khi sensor lỗi flags bit0=0, ESP32 không gửi hai khóa temperature/humidity. Khi RTC lỗi bit1=0, ESP32 để server gắn thời gian nhận. RTC và cloud dùng UTC; OLED cộng UTC+7.

Payload HTTP: `{"ts":<epoch_ms>,"values":{"temperature":25.3,"humidity":64.1,"sensor_ok":true,"rtc_ok":true,"sequence":42,"rssi":-60,"demo":false}}`. Device ID do token xác định, không cần phát token trong payload/log.

## Kiểm tra trên máy

```powershell
# Với C compiler sẵn có:
cc tests/test_protocol.c -o tests/protocol-test
# Trên máy hiện tại có Zig trong .tools:
.tools/ziglang/zig.exe cc tests/test_protocol.c -o tests/protocol-test.exe
tests/protocol-test.exe
python tests/check_artifacts.py
```

Các kiểm tra này không thay thế đo timing DHT, kiểm chứng memory XC8, kiểm tra điện áp hoặc import dashboard vào deployment thực tế.
