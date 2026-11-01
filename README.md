# Đồ án 2 — Giám sát nhiệt độ và độ ẩm qua Internet

Thiết kế đã thống nhất: **DHT11 → AT89S52 → OLED SSD1315**; **AT89S52 ↔ ESP32 → Wi-Fi/Internet → nền tảng IoT → dashboard web**.

- Mạch thật; AT89S52 phụ trách đo/hiển thị, ESP32 phụ trách mạng.
- OLED trắng 0,96 inch I²C, hai trang qua nút nhấn.
- Nền tảng có sẵn theo hướng ThingsBoard; dịch vụ cụ thể chưa chốt.
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
| AT89S52 — đọc DHT11, giờ từ ESP32, OLED, UART | [main.c](firmware/at89s52/main.c) |
| ESP32 — UART, Wi-Fi, HTTPS, NTP | [main.cpp](firmware/esp32/src/main.cpp) |
| Build, nạp và giao thức | [Hướng dẫn firmware](docs/firmware.md) |
| Dashboard native để import | [environment-monitor.json](dashboard/environment-monitor.json) |
| Tạo thiết bị, dashboard và alarm rules | [Hướng dẫn nền tảng](dashboard/README.md) |
| Tất cả linh kiện cần lắp/hàn | [BOM.md](hardware/BOM.md) / [BOM.csv](hardware/BOM.csv) |
| Sơ đồ nối dây | [Hình SVG](hardware/wiring.svg) / [Bảng chân chi tiết](hardware/wiring.md) |
| Kế hoạch và nguồn kỹ thuật | [Kế hoạch](docs/implementation-plan.md) / [Nguồn](docs/sources.md) |
| Giá linh kiện và PCB120.000đ | [Bảng giá](hardware/cost-estimate.md) / [CSV](hardware/cost-estimate.csv) |
| ThingsBoard thật trên máy | [Local demo](dashboard/local/README.md) — http://127.0.0.1:18080 |

## Chạy thử

1. Lắp và kiểm tra nguồn theo tài liệu phần cứng; chưa có PCB sản xuất tự động từ sơ đồ này.
2. Nạp AT89S52 bằng Burn-E với HEX được biên dịch từ đúng mã nguồn, chạy Verify rồi cắm AT89S52 vào mạch. File HEX đã build: `firmware/at89s52/release/environment-monitor.hex`; bạn tự chạy Verify trên chip bằng Burn-E. Build ESP32 bằng `pio run -d firmware/esp32 -e esp32c3`.
3. Tạo `firmware/esp32/include/secrets.h` từ file example; điền Wi-Fi, HTTPS host, device token và root CA. Không đưa credentials lên Git.
4. Tạo device `ENV-MONITOR-01`, import dashboard và cấu hình alarm rules theo hướng dẫn nền tảng.
5. Có thể dùng environment `demo` để phát dữ liệu giả có nhãn trước khi gắn AT89S52.

## Trạng thái kiểm tra

- ESP32 live và demo đã build trên máy phát triển; kiểm thử UART/calendar native và kiểm tra cấu trúc dashboard/BOM có trong `tests/`.
- Không dùng RTC/pin dự phòng. ESP32 lấy giờ NTP, gửi cho AT89S52 hiển thị UTC+7; khởi động chưa có mạng báo chưa đồng bộ.
- Đã chọn module TXS0108E: bốn kênh I²C/UART, OE từ GPIO6. Xem bảng chân trước khi lắp.
- AT89S52 đã build bằng SDCC trong giới hạn Flash/RAM; HEX và báo cáo tại `firmware/at89s52/release/`. Người dùng tự Verify bằng Burn-E; chưa kiểm thử mạch thật.
- Dashboard đã import và kiểm tra trên ThingsBoard CE cục bộ tại `http://127.0.0.1:18080`; dữ liệu có nhãn giả lập. Chưa kết nối mạch thật hoặc triển khai Internet. Xem [cách chạy/dừng demo](dashboard/local/README.md).
