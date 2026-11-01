# Kiểm tra bản triển khai — 2026-11-01

## Đã chạy trên máy phát triển

- PlatformIO `esp32c3`, đích C3 SuperMini với UART1/USB CDC: build thành công; RAM 40.188/327.680 byte, Flash 912.614/1.310.720 byte.
- PlatformIO `demo`, đích C3: build thành công; RAM 40.196/327.680 byte, Flash 912.760/1.310.720 byte.
- Native C `tests/test_protocol.c`: qua CRC-8/SMBUS, frame lỗi/checksum lỗi/đảo chữ số, overflow, flags, ngày nhuận/calendar; mirror thời gian chưa đồng bộ, hợp lệ, hết hạn và xóa khi T=0.
- `tests/check_artifacts.py`: 11 widget có alias đúng; các khóa telemetry/ngưỡng đầy đủ; BOM 38 reference không trùng trong 27 dòng, đã bỏ RTC ngoài và dùng TXS0108E.
- `hardware/wiring.svg`: XML hợp lệ.
- Review độc lập: đã sửa race khởi đầu phản hồi DHT11; đổi XOR thành CRC-8 để phát hiện lỗi đổi vị trí byte tốt hơn. Đã build/test lại sau khi sửa.
- ThingsBoard CE 4.3.1.8 + PostgreSQL 18 chạy thật trong Docker cục bộ. Dashboard import thành công, có dữ liệu mô phỏng được đánh dấu rõ; UI toàn tiếng Anh.
- Playwright trên Edge: biểu đồ đúng °C/%RH, không có page error; lưu ngưỡng high temperature=29 thành công qua UI, kiểm tra API rồi khôi phục 28. Native alarm history có bản ghi từ profile/rule chain riêng.
- Bảng giá bao phủ đủ 38 reference: các mục đã có giá + PCB120.000đ = 505.000đ; F1 chưa có giá đúng quy cách và chưa được cộng. Không biến giá giữ chỗ thành giá mua thực tế.

## Chưa kiểm chứng

- Theo yêu cầu người dùng, bỏ bước cài/build compiler PIC trên máy này. Quy trình nạp dùng Burn-E; chưa có HEX PIC đã kiểm chứng hoặc xác nhận bộ nhớ, stack/call depth và timing thực tế.
- Không có mạch thật: chưa đo điện áp, thạch anh, I²C/UART hoặc chạy màn OLED SSD1315.
- Chưa kết nối PIC/C3 thật với ThingsBoard hoặc triển khai HTTPS qua Internet; hiện chỉ demo localhost với dữ liệu giả lập.
- Chưa có schematic CAD/netlist/PCB đã ERC/DRC; SVG và bảng chân phục vụ lắp thử và bước thiết kế schematic tiếp theo.

Các giới hạn này được ghi trong README/hướng dẫn. Chưa nạp thiết bị hoặc tạo dịch vụ cloud ngoài. Tài khoản/thiết bị/profile/rule chain demo chỉ nằm trên ThingsBoard localhost.
