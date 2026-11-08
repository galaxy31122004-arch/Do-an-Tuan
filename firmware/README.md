# Firmware theo phiên bản

Mỗi phiên bản là một bản sao đầy đủ. Chỉ sửa thư mục mới nhất; thư mục cũ đóng băng.

| Thư mục | Phiên bản | Nội dung | Build |
|---|---|---|---|
| [v0.2.0](v0.2.0/) | 0.2.0 (chưa phát hành, đang sửa) | Thêm relay P2.0 (J6): tự bật ≥ 32,0 °C, tắt ≤ 30,0 °C, tắt khi lỗi cảm biến; cờ bit 2 trong frame M; OLED dòng RELAY; ESP32 gửi `relay` | AT89S52: `firmware/v0.2.0/at89s52/build.ps1`; ESP32: `pio run -d firmware/v0.2.0/esp32 -e esp32c3` |
| [v0.1.0](v0.1.0/) | 0.1.0 (đóng băng) | `at89s52/` (SDCC, HEX ở `release/`), `esp32/` (PlatformIO, ESP32-C3), `common/` (giao thức UART, đồng hồ) | AT89S52: `firmware/v0.1.0/at89s52/build.ps1`; ESP32: `pio run -d firmware/v0.1.0/esp32 -e esp32c3` |

Phiên bản mới: chép `v0.1.0/` sang `v<mới>/`, cập nhật đường dẫn trong README, docs, tests, `.gitignore` và `.gitattributes`, rồi ghi thêm dòng vào bảng này.
