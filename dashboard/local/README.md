# Local ThingsBoard demo

ThingsBoard CE 4.3.1.8 chạy thật trong Docker, PostgreSQL 18, chỉ mở tại **http://127.0.0.1:18080**. Dashboard: **ENV Monitor — ESP32-C3 · SIMULATED DATA**. Đăng nhập cục bộ: `tenant@thingsboard.org` / `tenant`. Dùng dữ liệu mô phỏng, chưa nối cảm biến thật.

## Đã cấu hình

- Thiết bị ENV-MONITOR-01; dashboard 11 widget, toàn bộ chữ giao diện bằng tiếng Anh.
- Profile ENV Monitor NTP với năm alarm rule, ngưỡng lấy từ server attributes.
- Rule chain ENV Monitor Processing riêng, có Device Profile node để thực thi alarm rule; không thay root chain của các thiết bị khác.
- Lịch sử demo, trạng thái hoạt động và luồng số đo mới mỗi 10 giây. `demo=true` trong mọi bản ghi giả lập.
- Dashboard được kiểm tra trên Edge bằng Playwright: số đo, biểu đồ đúng đơn vị °C/%RH, lịch sử, form ngưỡng và cảnh báo. Không có lỗi JavaScript trong lần kiểm tra.

## Chạy lại sau khi đã cài

```powershell
docker compose -f dashboard/local/compose.yml up -d
python dashboard/local/seed.py
python dashboard/local/seed.py --stream
```

Mở http://127.0.0.1:18080, đăng nhập rồi chọn dashboard. `--stream` chạy trong terminal; Ctrl+C để dừng. `session.json` chứa token thiết bị nên được bỏ khỏi Git. Script seed chỉ kết nối localhost, không đăng nhập hoặc tạo tài nguyên ở cloud ngoài.

Lần cài đầu trên máy khác cần tạo `.env` cùng thư mục chứa `TB_DB_PASSWORD=<mật khẩu tự chọn>` và chạy một lần:

```powershell
docker compose -f dashboard/local/compose.yml run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard
docker compose -f dashboard/local/compose.yml up -d
```

Không chạy lại bước install vào cơ sở dữ liệu đang dùng. Dữ liệu được giữ trong Docker volume của project. `seed.py` dùng tài khoản tenant demo mặc định của bản cài LOAD_DEMO, chỉ phù hợp môi trường local này.

## Dừng demo đang chạy nền

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*Do-an-Tuan*dashboard*local*seed.py*--stream*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId }
docker compose -f dashboard/local/compose.yml stop
```

Lệnh stop giữ nguyên dữ liệu. Chưa mở HTTP/HTTPS cho board qua LAN/Internet; địa chỉ `127.0.0.1` trên ESP32-C3 không trỏ về máy tính. Khi kết nối mạch thật, cần endpoint HTTPS mà board truy cập được, CA và device token như hướng dẫn firmware. Không trộn dữ liệu demo với kết quả thực nghiệm thật.

Nguồn cài đặt chính thức: https://thingsboard.io/docs/user-guide/install/docker/ (RSCH-20261101-0006).
