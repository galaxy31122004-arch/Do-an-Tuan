# Kiểm tra bản triển khai — 2026-11-01

## Đã chạy trên máy phát triển

- PlatformIO `esp32c3`, đích C3 SuperMini với UART1/USB CDC: build thành công; RAM 40.188/327.680 byte, Flash 912.622/1.310.720 byte.
- PlatformIO `demo`, đích C3: build thành công; RAM 40.196/327.680 byte, Flash 912.768/1.310.720 byte.
- Native C `tests/test_protocol.c`: qua CRC-8/SMBUS, frame lỗi/checksum lỗi/đảo chữ số, overflow, flags, ngày nhuận/calendar; mirror thời gian chưa đồng bộ, hợp lệ, hết hạn và xóa khi T=0.
- `tests/check_artifacts.py`: 11 widget có alias đúng; các khóa telemetry/ngưỡng đầy đủ; BOM 38 reference không trùng trong 27 dòng, đã bỏ RTC ngoài và dùng TXS0108E.
- `hardware/wiring.svg`: XML hợp lệ. File Intel HEX có checksum đúng, địa chỉ trong 8 KB, EOF hợp lệ và khớp hash nguồn/release; đây là kiểm tra file, không phải Burn-E Verify chip.
- Review độc lập: đã sửa race khởi đầu phản hồi DHT11; đổi XOR thành CRC-8 để phát hiện lỗi đổi vị trí byte tốt hơn. Đã build/test lại sau khi sửa.
- ThingsBoard CE 4.3.1.8 + PostgreSQL 18 chạy thật trong Docker cục bộ. Dashboard import thành công, có dữ liệu mô phỏng được đánh dấu rõ; UI toàn tiếng Anh.
- Playwright trên Edge: biểu đồ đúng °C/%RH, không có page error; lưu ngưỡng high temperature=29 thành công qua UI, kiểm tra API rồi khôi phục 28. Native alarm history có bản ghi từ profile/rule chain riêng.
- Bảng giá bao phủ đủ 38 reference: các mục đã có giá + PCB120.000đ = 403.500đ; F1 chưa có giá đúng quy cách và chưa được cộng. Không biến giá giữ chỗ thành giá mua thực tế.

- AT89S52: SDCC mcs51 small, 11,0592 MHz/12T, Flash 7.276/8.192 byte, không dùng RAM ngoài; vùng stack ban đầu 52 byte. HEX và hash nguồn tại `firmware/v0.2.0/at89s52/release/`.
- uCsim C52: chạy 2.000.000 lệnh, xuất các frame đo lỗi cảm biến có CRC đúng; CPU vẫn chạy. Tiêm frame S/T hoàn chỉnh vào bộ đệm, ép hai trang OLED với ACK giả trong bộ nhớ mô phỏng: stack cao nhất 0xF0 (còn 15 byte), không tràn. Đây chưa phải kiểm tra RX UART điện thực hay mọi đường ngắt.
- DHT11: vòng bắt xung bằng assembly đã thay phần C gây trễ giữa hai cạnh. Mô phỏng 40 bit 65/0/25/0/90 với xung 26/70, 22/65 và 30/75 µs giải mã đúng `41 00 19 00 5A`.
- Review độc lập sau sửa: không còn lỗi firmware quan trọng được phát hiện; cần tiếp tục thử UART RX, DHT/TXS/OLED trên phần cứng.
- Burn-E Programmer 9.00.88: đã xác nhận danh sách AT89S52 và bảng chân. Dừng thao tác khi người dùng chọn tự Verify; không nạp/xóa chip.

## Chưa kiểm chứng

- Người dùng tự nạp/Verify AT89S52 bằng Burn-E. Chưa có Verify PASS trên chip thật, hoặc kiểm tra mọi đường chạy/stack/timing bằng logic analyzer.
- Không có mạch thật: chưa đo điện áp, thạch anh, I²C/UART hoặc chạy màn OLED SSD1315.
- Chưa kết nối AT89S52/C3 thật với ThingsBoard hoặc triển khai HTTPS qua Internet; hiện chỉ demo localhost với dữ liệu giả lập.
- Chưa có schematic CAD/netlist/PCB đã ERC/DRC; SVG và bảng chân phục vụ lắp thử và bước thiết kế schematic tiếp theo.

Các giới hạn này được ghi trong README/hướng dẫn. Chưa nạp thiết bị hoặc tạo dịch vụ cloud ngoài. Tài khoản/thiết bị/profile/rule chain demo chỉ nằm trên ThingsBoard localhost.
