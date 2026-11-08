# Build, cấu hình và kiểm thử firmware

## Phần cứng mặc định

AT89S52 DIP-40 / 11,0592 MHz / 5 V; DHT11 P3.2/12; nút trang P3.3/13; I²C phần mềm SDA P1.0/1, SCL P1.1/2 (dưới 100 kHz); UART TX P3.1/11, RX P3.0/10, 9600 8N1. ESP32-C3 SuperMini RX GPIO4, TX GPIO3, OE TXS0108E GPIO0. Xem `hardware/wiring.md`.

## ESP32 — PlatformIO

Đích hiện tại là ESP32-C3 SuperMini 4 MB: dùng cấu hình chip `esp32-c3-devkitm-1` với USB CDC làm console. UART1 nối AT89S52 tại RX=GPIO4, TX=GPIO3; OE=GPIO0. Không dùng Serial2 hoặc sơ đồ chân WROOM cũ. Nếu lần đầu chưa thấy cổng USB để nạp, giữ BOOT, nhấn/thả RESET rồi thả BOOT để vào download mode theo board thực tế. Chừa GPIO18/19 cho USB; không dùng chân strap GPIO2/8/9 cho UART/OE trong thiết kế này.

```powershell
Copy-Item firmware/v0.2.0/esp32/include/secrets.example.h firmware/v0.2.0/esp32/include/secrets.h
# Điền Wi-Fi, HTTPS origin, device token và CA trong secrets.h.
pio run -d firmware/v0.2.0/esp32 -e esp32c3
pio run -d firmware/v0.2.0/esp32 -e esp32c3 -t upload --upload-port COM6
pio device monitor -b 115200 --port COM6
```

Thay COM6 bằng cổng thực tế; lệnh upload chỉ chạy khi người dùng đã nối đúng board. Environment `demo` tạo số liệu giả, đánh dấu telemetry `demo=true`; không cần AT89S52 cho bài thử cloud. Bản live luôn phát `demo=false`.

Firmware gửi tối đa một bản ghi mới mỗi 10 giây; chờ frame AT89S52 mới sau khi Wi-Fi kết nối lại. HTTPS có timeout, UART chạy task riêng và queue chỉ chứa một bản mới nhất. Lỗi gửi không tạo backlog. ESP32 lấy giờ NTP và gửi UTC cho AT89S52 khoảng mỗi giây; khi chưa đồng bộ thì gửi 0 để AT89S52 báo TIME NOT SYNCED. AT89S52 chỉ giữ bản giờ hiển thị, đánh dấu hết hạn sau 600 vòng lặp không nhận cập nhật (khoảng vài giây). Khi mất Internet nhưng còn nguồn, ESP32 vẫn duy trì giờ đã đồng bộ và tiếp tục gửi cho AT89S52. Mất điện rồi bật lại cần NTP; không có pin giữ giờ. ESP32 gắn timestamp UTC lúc nhận frame đo từ AT89S52. Bộ ESP32 Arduino hiện dùng time_t 32-bit, vì vậy cần nâng toolchain trước mốc năm 2038.

## AT89S52 — nạp HEX bằng Burn-E

Đã chuyển mã sang SDCC cho họ 8051, không dùng XC8. File nạp: [`environment-monitor.hex`](../firmware/v0.2.0/at89s52/release/environment-monitor.hex). Burn-E là phần mềm nạp/so sánh Flash trên chip, không biên dịch C hay kiểm chứng logic firmware. Người dùng sẽ tự thực hiện Verify; chưa có kết quả nạp/Verify phần cứng.

1. Mở Burn-E Programmer 9.00.88, chọn family **AT89S**, device **AT89S52** (không chọn AT89LS51/52). Phiên làm việc đã chọn AT89S52.
2. Tắt nguồn target, nối theo mục J3 trong `hardware/wiring.md`. Cần thạch anh ngoài 11,0592 MHz và EA chân 31 nối +5 V; không giả định một đế ZIF trần đã có đủ các kết nối.
3. Mở HEX nói trên; không dùng config HS/LVP/VPP của PIC. Giữ Mode 1 / no program lock trong lúc kiểm tra để còn đọc/verify Flash.
4. Xác nhận mạch nạp được nhận, chỉ chọn một nguồn target phù hợp. Chạy Write theo hướng dẫn Burn-E, bật Verify After Write rồi kiểm tra thông báo; có thể chạy Verify riêng để so sánh lại. Không đổi lock bits khi chưa cần.
5. Chỉ ghi nhận Verify PASS khi phần mềm đã đọc và so sánh đúng chip thật. Ngắt nguồn trước khi tháo IC/cáp. Kiểm tra cảm biến, OLED, UART và Wi-Fi riêng sau khi nạp.

J3: 1 RST/9; 2 +5V/40; 3 GND/20; 4 MISO P1.6/7; 5 SCK P1.7/8; 6 MOSI P1.5/6. RST tích cực cao; không đưa điện áp VPP của PIC vào mạch. Pinout này đã đối chiếu phần hướng dẫn AT89S52 trong Burn-E đang mở; vẫn kiểm tra chiều đầu cắm thực tế.

### Biên dịch lại khi sửa mã

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File firmware/v0.2.0/at89s52/build.ps1 -SdccPath .tools/sdcc-portable/sdcc/bin/sdcc.exe
```

Script yêu cầu SDCC có thư viện mcs51 small, kiểm tra giới hạn Flash 8 KB/RAM trong và tạo HEX cùng báo cáo/hash nguồn. Cấu hình build, dung lượng và giới hạn kiểm tra nằm tại `release/build-info.json` và `release/memory.txt`. Không dùng model large hoặc RAM ngoài: PCB không có XRAM. Chưa xác nhận timing cảm biến/stack ở mọi đường chạy trên chip thật.

Driver OLED dùng font chữ hoa 5×7 và truyền từng dòng, không cần framebuffer 1.024 byte. Hiển thị hai trang qua nút nhấn chống dội; thông báo mạng trên AT89S52 hết hạn nếu không nhận trạng thái ESP32. `LAST SEND` là thời gian ESP32 nhận HTTP 2xx, không khẳng định mọi widget đã cập nhật. OLED dùng địa chỉ 0x3C; chỉnh `board.h` nếu module là 0x3D. Bộ lệnh khởi tạo cần kiểm tra trên SSD1315 thực tế; không coi build là bằng chứng màn hình đã hoạt động.

AT89S52 vẫn đo khi Internet mất. Mọi chờ DHT/I²C có giới hạn; lỗi cảm biến không trở thành số đo 0 hợp lệ. Việc mất nguồn AT89S52/ESP32 hoặc bus I²C bị chập cần thử trực tiếp trong nghiệm thu; đây chưa phải hệ thống công nghiệp tự phục hồi đã kiểm định.

## Giao thức UART

ASCII, kết thúc LF, payload có CRC-8/SMBUS viết hai ký tự hex (polynomial 0x07, init 0, không reflect, xorout 0). Không đưa khoảng trắng vào frame.

```text
$M,sequence,epochUTC,temperature10,humidity10,flags*XX\n
$S,wifiOK,cloudOK,lastSuccessEpochUTC*XX\n
$T,epochUTC*XX\n
```

Checksum tính trên phần giữa `$` và `*`, không gồm hai dấu đó. Nhiệt độ/độ ẩm theo đơn vị 0,1; flags bit0 = sensor valid, bit1 = time valid. Khi sensor lỗi flags bit0=0, ESP32 không gửi hai khóa temperature/humidity. Khi nhận frame, ESP32 gắn thời gian của nó nếu đã đồng bộ và cập nhật bit1; AT89S52 dùng giờ phản chiếu từ frame T cho OLED. T=0 hoặc cập nhật quá hạn sẽ xóa trạng thái giờ hợp lệ. Cloud dùng UTC; OLED cộng UTC+7.

Payload HTTP: `{"ts":<epoch_ms>,"values":{"temperature":25.3,"humidity":64.1,"sensor_ok":true,"time_ok":true,"sequence":42,"rssi":-60,"demo":false}}`. Device ID do token xác định, không cần phát token trong payload/log.

## Kiểm tra trên máy

```powershell
# Với C compiler sẵn có:
cc tests/test_protocol.c -o tests/protocol-test
# Trên máy hiện tại có Zig trong .tools:
.tools/ziglang/zig.exe cc tests/test_protocol.c -o tests/protocol-test.exe
tests/protocol-test.exe
python tests/check_artifacts.py
# Sau build AT89S52, kiểm tra mô phỏng lệnh 8051 (không điều khiển Burn-E):
python tests/test_at89s52_sim.py --s51 .tools/sdcc-portable/sdcc/bin/s51.exe
```

Các kiểm tra này không thay thế đo timing DHT, Verify chip AT89S52 bằng Burn-E, kiểm tra điện áp hoặc import dashboard vào deployment thực tế. HEX đã biên dịch không thay thế kiểm thử chức năng trên mạch thật.
