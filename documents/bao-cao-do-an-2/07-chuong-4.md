# CHƯƠNG 4. THI CÔNG, KIỂM THỬ VÀ ĐÁNH GIÁ

Tại thời điểm hoàn thành báo cáo, mạch thật chưa được chế tạo. Chương này trình bày quy trình thi công, nạp chương trình và kế hoạch kiểm thử. Kết quả đo trên mạch thật sẽ được bổ sung sau khi chế tạo.

## 4.1. Quy trình thi công

1. Đo khoảng cách hai hàng chân của module ESP32-C3 SuperMini và TXS0108E thật, đối chiếu footprint; nếu lệch thì sửa footprint, đi lại dây đoạn liên quan và chạy lại DRC.
2. Xuất tệp Gerber và tệp khoan từ KiCad để đặt in mạch hai lớp 92,5 × 84,7 mm.
3. Hàn linh kiện theo thứ tự từ thấp đến cao:
   - điện trở, diode (R8, R9 nằm dưới module TXS0108E nên hàn sát mặt bo);
   - đế IC, header;
   - tụ, thạch anh, nút nhấn;
   - relay, cầu đấu, jack DC;
   - LM7805, vít tab xuống vùng đồng GND.
4. Chưa cắm AT89S52 và các module. Kiểm tra nguồn trước theo mục 4.3.

## 4.2. Nạp chương trình

- **AT89S52:**
  - Biên dịch `main.c` bằng SDCC để tạo tệp HEX.
  - Nạp và kiểm tra lại (verify) bằng mạch nạp Burn-E. Cách nạp chính là đặt chip vào đế của mạch nạp; cổng ISP J3 trên bo dùng cho trường hợp nạp tại chỗ.
- **ESP32-C3:**
  - Điền thông tin Wi-Fi, địa chỉ máy chủ, token thiết bị và chứng chỉ CA vào `secrets.h`.
  - Biên dịch và nạp qua cổng USB-C bằng PlatformIO, khi bo **chưa** cấp nguồn 12 V.
- **ThingsBoard:**
  - Tạo thiết bị `ENV-MONITOR-01` và import dashboard.
  - Tạo bốn thuộc tính ngưỡng và cấu hình luật cảnh báo trong hồ sơ thiết bị.

## 4.3. Kế hoạch kiểm thử

**Bảng 4.1. Kịch bản kiểm thử trên mạch thật**

| STT | Hạng mục | Cách thực hiện | Tiêu chí đạt |
|---|---|---|---|
| 1 | Ngắn mạch nguồn | Đo điện trở giữa +12V, +5V, +3V3 và GND khi chưa cấp nguồn | Không có ngắn mạch |
| 2 | Chống ngược cực | Cấp 12 V ngược cực qua nguồn có giới hạn dòng | Mạch không nhận điện, không hỏng linh kiện |
| 3 | Điện áp nguồn | Cấp 12 V, đo TP1, TP2 | +5V nằm trong 4,75–5,25 V; +3V3 khoảng 3,3 V |
| 4 | Nhiệt LM7805 | Chạy liên tục 30 phút khi Wi-Fi hoạt động, đo nhiệt độ tab | Tab không quá khoảng 80 °C |
| 5 | Dao động, reset | Cắm AT89S52, đo dao động ở chân XTAL, nhấn SW2 | Có dao động 11,0592 MHz; chương trình khởi động lại |
| 6 | OLED | Quan sát màn hình sau khi ESP32 bật OE | Hiện trang 0 đúng bố cục |
| 7 | DHT11 | So số đo với nhiệt ẩm kế tham chiếu ở nhiều thời điểm | Sai lệch trong sai số công bố của DHT11 |
| 8 | Lỗi cảm biến | Rút DHT11 | OLED báo SENSOR ERROR; relay tắt; cloud nhận `sensor_ok = false` |
| 9 | Nút đổi trang | Nhấn SW1 nhiều lần | Chuyển trang đúng, không nhảy hai lần |
| 10 | UART | Theo dõi Serial ESP32 hoặc dùng logic analyzer | Khung M khoảng 2 s/lần; không có lỗi CRC |
| 11 | NTP và giờ | Bật Wi-Fi | OLED hiện ngày giờ UTC+7 đúng |
| 12 | Gửi cloud | Theo dõi dashboard | Có bản ghi mới khoảng 10 s/lần; HTTP 2xx |
| 13 | Mất mạng | Tắt router rồi bật lại | OLED báo OFFLINE; vẫn đo và hiển thị; tự kết nối lại |
| 14 | Relay | Làm nóng cảm biến lên trên 32 °C rồi để nguội dưới 30 °C | Relay bật ở ≥ 32 °C, nhả ở ≤ 30 °C; tải qua NO đóng/cắt đúng |
| 15 | Cảnh báo | Đặt ngưỡng thấp hơn giá trị hiện tại trên dashboard | Cảnh báo được tạo, rồi tự xóa khi trở lại trong ngưỡng |
| 16 | Xuất CSV | Chọn khoảng thời gian và xuất dữ liệu | Tệp CSV có đúng các cột và khoảng thời gian đã chọn |

## 4.4. Kết quả

Kết quả kiểm thử phần mềm (Chương 3, mục 3.6) đã đạt. Kết quả kiểm thử trên mạch thật theo Bảng 4.1 sẽ được cập nhật sau khi chế tạo, bao gồm:

- ảnh mạch thật;
- số đo điện áp;
- bảng so sánh số đo DHT11 với thiết bị tham chiếu;
- ảnh chụp dashboard với dữ liệu thật.

## 4.5. Đánh giá

**Ưu điểm của thiết kế:**

- Phân chia rõ vai trò: AT89S52 đo, hiển thị và điều khiển; ESP32-C3 lo kết nối mạng. Mất mạng không ảnh hưởng chức năng tại chỗ.
- Giao thức khung có CRC giúp phát hiện lỗi truyền.
- Chuyển mức logic bằng TXS0108E, chân OE được điều khiển theo trình tự khi khởi động.
- Relay tách nguồn 12 V, điều khiển qua opto, mặc định tắt khi reset và khi cảm biến lỗi.
- Dữ liệu giả lập luôn được đánh dấu rõ, không lẫn với số đo thật.

**Hạn chế:**

- DHT11 có độ chính xác và dải đo hạn chế.
- Bản ghi trong thời gian mất mạng không được lưu bù.
- LM7805 tỏa nhiệt đáng kể khi cấp nguồn 12 V.
- Ngưỡng relay cố định trong firmware, chưa chỉnh được từ dashboard.
- Chưa có số liệu đo trên mạch thật.
