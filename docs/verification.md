# Kiểm tra bản triển khai — 2026-11-01

## Đã chạy trên máy phát triển

- PlatformIO `esp32dev`, sau khi thêm OE GPIO27: build thành công; RAM 46.824/327.680 byte, Flash 920.309/1.310.720 byte.
- PlatformIO `demo`: build thành công; RAM 46.832/327.680 byte, Flash 920.477/1.310.720 byte.
- Native C `tests/test_protocol.c`: qua kiểm tra CRC-8/SMBUS vector, frame lỗi/checksum lỗi/đảo vị trí chữ số, overflow, flags, ngày nhuận và giới hạn calendar.
- `tests/check_artifacts.py`: 11 widget có alias đúng; các khóa telemetry/ngưỡng đầy đủ; BOM 43 reference không trùng trong 31 dòng, dùng module TXS0108E.
- `hardware/wiring.svg`: XML hợp lệ.
- Review độc lập: đã sửa race khởi đầu phản hồi DHT11; đổi XOR thành CRC-8 để phát hiện lỗi đổi vị trí byte tốt hơn. Đã build/test lại sau khi sửa.

## Chưa kiểm chứng

- Theo yêu cầu người dùng, bỏ bước cài/build compiler PIC trên máy này. Quy trình nạp dùng Burn-E; chưa có HEX PIC đã kiểm chứng hoặc xác nhận bộ nhớ, stack/call depth và timing thực tế.
- Không có mạch thật: chưa đo điện áp, thạch anh, I²C/UART hoặc chạy màn OLED SSD1315.
- Không có tenant/URL/token: chưa import dashboard hoặc chạy các alarm rules trên ThingsBoard/Core IoT thực tế.
- Chưa có schematic CAD/netlist/PCB đã ERC/DRC; SVG và bảng chân phục vụ lắp thử và bước thiết kế schematic tiếp theo.

Các giới hạn này được ghi rõ trong README/hướng dẫn. Chưa nạp thiết bị, triển khai cloud hoặc phát sinh tài khoản dịch vụ.
