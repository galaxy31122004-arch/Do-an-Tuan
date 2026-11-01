# Phương án đã chọn: module TXS0108E

Người dùng đã chọn một module TXS0108E để chuyển mức giữa PIC/DS1307 5 V và OLED/ESP32 3,3 V. BOM, bảng chân, SVG và firmware ESP32 dùng chung phương án này.

TI công bố hỗ trợ open-drain và push-pull, VCCA 1,4–3,6 V, VCCB 1,65–5,5 V và VCCA ≤ VCCB. Với mạch này: A=3,3 V, B=5 V. Module cần dây ngắn, nguồn lọc tốt và OE điều khiển đúng mức VCCA.

## Ánh xạ thay thế

| Kênh TXS0108E | Phía A (3,3 V) | Phía B (5 V) |
|---|---|---|
| A1/B1 | OLED SDA | PIC RC4 chân 23 + DS1307 SDA chân 5 |
| A2/B2 | OLED SCL | PIC RC3 chân 18 + DS1307 SCL chân 6 |
| A3/B3 | ESP32 GPIO16 RX | PIC RC6 TX chân 25 |
| A4/B4 | ESP32 GPIO17 TX | PIC RC7 RX chân 26 |

GND chung; VCCA=3,3 V; VCCB=5 V. OE nối ESP32 GPIO27 và R4 100 kΩ xuống GND. Firmware giữ OE thấp, chờ 100 ms cho nguồn ổn định rồi bật; kiểm tra module không kéo cứng OE lên nguồn. C3 lọc VCCB, C13 lọc VCCA. Không cấp 5 V vào OE/GPIO27; không thêm chia áp vào đường đã qua TXS.

Đã bỏ cặp MOSFET, buffer và chia áp cũ; U4 nay là module TXS0108E. Không lắp bốn pull-up bus cũ vì TXS có pull-up nội; đối chiếu pull-up có sẵn trên OLED/module và đo tín hiệu. J5A/J5B dự kiến hai header 1x10, phải đo module thực tế. Các kênh còn lại để NC.

Nguồn chính thức: [TI TXS0108E](https://www.ti.com/product/TXS0108E), datasheet trên cùng trang. Thông số hãng đã đọc ngày 2026-11-01 (RSCH-20261101-0005). Việc chuyển module cụ thể vẫn cần đo tín hiệu trên mạch.
