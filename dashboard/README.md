# Dashboard ThingsBoard

File **`environment-monitor.json`** là dashboard native để import vào nền tảng, không phải một website/backend riêng. Có 11 widget: nhiệt độ, độ ẩm, hoạt động, hai biểu đồ, bảng lịch sử, form bốn ngưỡng, bảng cảnh báo, tình trạng cảm biến/đồng bộ thời gian và dấu hiệu dữ liệu giả lập.

## 1. Tạo thiết bị và cấu hình firmware

1. Đăng nhập bằng tài khoản tenant có quyền quản lý thiết bị/dashboard. Tạo device tên chính xác **ENV-MONITOR-01**, transport mặc định có hỗ trợ HTTP. Mỗi thiết bị được nhận diện bởi device access token; không dùng JWT tài khoản người dùng thay token thiết bị.
2. Sao chép `firmware/v0.2.0/esp32/include/secrets.example.h` thành `secrets.h`. Điền SSID, mật khẩu, HTTPS origin, token thiết bị và PEM root CA của domain. Token không xuất hiện trong dashboard JSON và không commit vào Git.
3. Build/nạp ESP32. Serial Monitor 115200 sẽ báo HTTP 2xx khi nền tảng nhận bản ghi. Không dùng `setInsecure()` để bỏ kiểm tra TLS. Firmware cần Internet/NTP để xác thực thời gian chứng chỉ.
4. Nền tảng đã chọn: ThingsBoard. Bản demo thật chạy cục bộ bằng Docker, xem `local/README.md`. Firmware thiết bị vẫn dùng HTTPS với CA/token của deployment khi kết nối mạch thật.

## 2. Import dashboard

1. Dashboards → Add/import dashboard → chọn `environment-monitor.json`.
2. Mở Edit → Entity aliases: alias `ENV-MONITOR-01` tìm device theo tên. Nếu không có dữ liệu, chọn lại đúng thiết bị và lưu. Không để alias trỏ vào dữ liệu ví dụ.
3. Chọn time window ở thanh công cụ: mặc định một giờ; chuyển sang History và chọn mốc bắt đầu/kết thúc để tra cứu.
4. Widget bảng và biểu đồ bật data export; dùng menu widget để xuất CSV nếu phiên bản/quyền đang dùng hỗ trợ. Giới hạn mặc định 2.000 bản ghi/query; xuất khoảng dài cần chia cửa sổ hoặc tăng giới hạn theo khả năng server. Không coi CSV bị giới hạn là toàn bộ lịch sử.
5. Biểu đồ dùng các điểm đo thay cho nối thẳng qua khoảng mất mạng. Thẻ số đo có thời gian cập nhật; khi cảm biến lỗi, số cũ có thể còn được nền tảng lưu, phải đọc cùng thẻ `sensor_ok`.

## 3. Thiết lập cảnh báo trên nền tảng

Import dashboard **không tự tạo alarm rules**. Để bảng cảnh báo hoạt động, tạo device profile riêng cho ENV-MONITOR-01 và cấu hình các alarm rule dưới đây; không đổi profile dùng chung của thiết bị khác. Ngưỡng là server attributes, không gửi xuống AT89S52.

Tại device → Attributes → Server attributes, tạo bốn khóa số `temperature_min`, `temperature_max`, `humidity_min`, `humidity_max`. Điền ngưỡng phù hợp với yêu cầu bài thí nghiệm. Form trên dashboard chỉnh đúng bốn khóa này; luôn giữ min < max. Đây là ngưỡng do người dùng đặt, không phải giới hạn an toàn của kho/nông nghiệp.

| Loại cảnh báo | Điều kiện tạo | Điều kiện xóa |
|---|---|---|
| Temperature high | `sensor_ok = true` và `temperature > temperature_max` | `sensor_ok = true` và `temperature <= temperature_max` |
| Temperature low | `sensor_ok = true` và `temperature < temperature_min` | `sensor_ok = true` và `temperature >= temperature_min` |
| Humidity high | `sensor_ok = true` và `humidity > humidity_max` | `sensor_ok = true` và `humidity <= humidity_max` |
| Humidity low | `sensor_ok = true` và `humidity < humidity_min` | `sensor_ok = true` và `humidity >= humidity_min` |
| Sensor fault | `sensor_ok = false` | `sensor_ok = true` |

Trong Device profile → Alarm rules, chọn giá trị so sánh **dynamic value → Server attribute** cho mỗi khóa ngưỡng, thay vì gõ cứng ngưỡng vào rule. Chọn severity và duration phù hợp bài demo, lưu rồi gán profile cho device. Nếu bản nền tảng không hỗ trợ giá trị động trong profile, dùng rule chain để đọc server attributes, so sánh rồi Create/Clear Alarm; không để form thay đổi mà rule vẫn dùng hằng số.

Đặt inactivity timeout của device khoảng 60 giây trong cấu hình nền tảng (lớn hơn chu kỳ gửi 10 giây) và kiểm tra server attribute `active`. Thẻ hoạt động phản ánh timeout của server, không thể phát hiện mất điện tức thời. Cảnh báo lỗi cảm biến không tự xóa cảnh báo vượt ngưỡng bằng một giá trị 0 giả.

## 4. Kiểm tra nghiệm thu

- Dùng env `demo` để kiểm tra kết nối trước khi có AT89S52: widget `demo` phải hiện true. Các số này là giả lập và không được ghi thành kết quả cảm biến.
- Dùng env `esp32c3` với AT89S52: `demo=false`, `sensor_ok=true`, `time_ok=true`; đối chiếu số đo OLED và dashboard.
- Thử thay ngưỡng qua dashboard để tạo rồi xóa cảnh báo, xác nhận bảng có lịch sử.
- Ngắt Internet trên thiết bị: OLED vẫn chạy; sau timeout thẻ active đổi false; kết nối lại chỉ có bản ghi mới.
- Tháo DHT11: sensor_ok=false; không có nhiệt độ/độ ẩm giả 0 được thêm vào lịch sử.

## Tính tương thích và nguồn

JSON được tạo từ schema/widget mặc định trong mã nguồn ThingsBoard chính thức (RSCH-20261101-0003), đã import và xem bằng trình duyệt trên ThingsBoard CE 4.3.1.8 cục bộ. Bản cũ thiếu `system.cards.value_card` hoặc `system.time_series_chart` cần thay bằng widget tương đương qua editor. `generate.py` tạo lại file từ upstream khi có mạng; file JSON đi kèm đã tạo sẵn, không cần chạy generator để import. Script `local/seed.py` còn tạo profile có năm alarm rule và rule chain xử lý riêng cho thiết bị demo; import dashboard ở server khác vẫn cần cấu hình profile/chain theo phần 3.

Mã nguồn widget tham chiếu thuộc ThingsBoard Authors, Apache License 2.0: https://github.com/thingsboard/thingsboard . Dashboard chỉ dùng các widget hệ thống đã cài trên server, không nhúng mã controller của bên thứ ba.
