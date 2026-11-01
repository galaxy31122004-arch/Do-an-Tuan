# Đồ án 2 — Giám sát nhiệt độ và độ ẩm qua Internet

Thiết kế đã thống nhất: **DHT11 + DS1307 → PIC16F877A → OLED SSD1315**; **PIC ↔ ESP32 → Wi-Fi/Internet → nền tảng IoT → dashboard web**.

- Mạch thật; PIC phụ trách đo/hiển thị, ESP32 phụ trách mạng.
- OLED trắng 0,96 inch I²C, hai trang qua nút nhấn.
- Nền tảng có sẵn theo hướng Core IoT/ThingsBoard; dịch vụ cụ thể chưa chốt.
- Dashboard: số đo mới nhất, biểu đồ, lịch sử, lọc thời gian, CSV và cảnh báo ngưỡng.
- Mất mạng vẫn đo tại chỗ; tự kết nối lại, chưa lưu bù.

## Tài liệu

- Bản gốc: [Tóm tắt đề tài](TÓM%20TẮT%20ĐỀ%20TÀI%20ĐỒ%20ÁN%202.docx).
- Bản cập nhật: [Tóm tắt IoT OLED](TÓM%20TẮT%20ĐỀ%20TÀI%20ĐỒ%20ÁN%202%20-%20IoT%20OLED.docx).
- [Cấu trúc tài liệu](01-cau-truc-tong-the.md) và [phạm vi đã xác nhận](02-yeu-cau-thong-tin.md).

## Workspace

AXON lưu trạng thái tại `.planning/state.json`; bối cảnh, kiến trúc và quy ước tại `.planning/project/`. Planning có repository riêng và lịch sử tự lưu cục bộ. Chưa cấu hình remote.

## Firmware, dashboard và phần cứng

| Thành phần | Tệp / hướng dẫn |
|---|---|
| PIC16F877A — đọc DHT11/RTC, OLED, UART | [main.c](firmware/pic/main.c) |
| ESP32 — UART, Wi-Fi, HTTPS, NTP | [main.cpp](firmware/esp32/src/main.cpp) |
| Build, nạp và giao thức | [Hướng dẫn firmware](docs/firmware.md) |
| Dashboard native để import | [environment-monitor.json](dashboard/environment-monitor.json) |
| Tạo thiết bị, dashboard và alarm rules | [Hướng dẫn nền tảng](dashboard/README.md) |
| Tất cả linh kiện cần lắp/hàn | [BOM.md](hardware/BOM.md) / [BOM.csv](hardware/BOM.csv) |
| Sơ đồ nối dây | [Hình SVG](hardware/wiring.svg) / [Bảng chân chi tiết](hardware/wiring.md) |
| Kế hoạch và nguồn kỹ thuật | [Kế hoạch](docs/implementation-plan.md) / [Nguồn](docs/sources.md) |

## Chạy thử

1. Lắp và kiểm tra nguồn theo tài liệu phần cứng; chưa có PCB sản xuất tự động từ sơ đồ này.
2. Build PIC với MPLAB XC8. Build ESP32 bằng `pio run -d firmware/esp32 -e esp32dev`.
3. Tạo `firmware/esp32/include/secrets.h` từ file example; điền Wi-Fi, HTTPS host, device token và root CA. Không đưa credentials lên Git.
4. Tạo device `ENV-MONITOR-01`, import dashboard và cấu hình alarm rules theo hướng dẫn nền tảng.
5. Có thể dùng environment `demo` để phát dữ liệu giả có nhãn trước khi gắn PIC.

## Trạng thái kiểm tra

- ESP32 live và demo đã build trên máy phát triển; kiểm thử UART/calendar native và kiểm tra cấu trúc dashboard/BOM có trong `tests/`.
- Chưa có XC8 trên máy nên chưa xác nhận build, bộ nhớ hoặc timing PIC. Chưa nạp lên mạch thật.
- Chưa import vào tenant thật. Dashboard cần thiết bị, root CA, token và alarm rules của deployment thực tế; không có tài khoản hoặc tài nguyên cloud nào được tạo tự động.
