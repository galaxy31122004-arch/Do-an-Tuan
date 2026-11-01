# Kiểm tra bản triển khai — 2026-11-01

## Đã chạy trên máy phát triển

- PlatformIO `esp32dev`: build thành công; RAM 46.824/327.680 byte, Flash 918.281/1.310.720 byte.
- PlatformIO `demo`: build thành công; RAM 46.832/327.680 byte, Flash 918.433/1.310.720 byte.
- Native C `tests/test_protocol.c`: qua kiểm tra CRC-8/SMBUS vector, frame lỗi/checksum lỗi/đảo vị trí chữ số, overflow, flags, ngày nhuận và giới hạn calendar.
- `tests/check_artifacts.py`: 11 widget có alias đúng; các khóa telemetry/ngưỡng đầy đủ; BOM 48 reference không trùng trong 33 dòng.
- `hardware/wiring.svg`: XML hợp lệ.
- Review độc lập: đã sửa race khởi đầu phản hồi DHT11; đổi XOR thành CRC-8 để phát hiện lỗi đổi vị trí byte tốt hơn. Đã build/test lại sau khi sửa.

## Chưa kiểm chứng

- Không có XC8: chưa biên dịch PIC hoặc xác nhận RAM, program memory, stack/call depth và timing thực tế.
- Không có mạch thật: chưa đo điện áp, thạch anh, I²C/UART hoặc chạy màn OLED SSD1315.
- Không có tenant/URL/token: chưa import dashboard hoặc chạy các alarm rules trên ThingsBoard/Core IoT thực tế.
- Chưa có schematic CAD/netlist/PCB đã ERC/DRC; SVG và bảng chân phục vụ lắp thử và bước thiết kế schematic tiếp theo.

Các giới hạn này được ghi rõ trong README/hướng dẫn. Chưa nạp thiết bị, triển khai cloud hoặc phát sinh tài khoản dịch vụ.
