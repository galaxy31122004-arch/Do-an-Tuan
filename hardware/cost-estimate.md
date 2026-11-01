# Dự toán mua linh kiện và in PCB — 1 bộ

Ngày tra giá: **01/11/2026**. Phiên bản PIC16F877A + ESP32-C3 SuperMini + TXS0108E + OLED SSD1315, dùng NTP; không có RTC/pin dự phòng.

- Linh kiện đã có giá: **385.000đ**.
- In PCB theo giá bạn cung cấp: **120.000đ**.
- **Tạm tính tiền mua: 505.000đ, chưa gồm F1 và các khoản ngoài phạm vi bên dưới.**

Tính theo đơn vị bán thực tế, gồm gói trở 50 con, gói LED 100 con và gói nút 10 con; phần dư giữ lại cho các mạch sau. Đây là giá niêm yết tham khảo, không phải xác nhận đặt hàng hoặc cam kết còn hàng.

| Mục | Số đơn vị mua | Giá/đơn vị mua | Thành tiền | Ghi chú / nguồn |
|---|---:|---:|---:|---|
| U1: PIC16F877A DIP-40 | 1 | 129.000đ | 129.000đ | 1 IC; RSCH-20261101-0009 [U1](https://chotroihn.vn/pic-16f877a-ip-dip40) |
| U2: ESP32-C3 SuperMini 4MB | 1 | 75.000đ | 75.000đ | 1 board; RSCH-20261101-0009 [U2](https://icdayroi.com/kit-phat-trien-wifi-bluetooth-esp32-c3-super-mini-4mb) |
| U4: Module TXS0108E | 1 | 15.000đ | 15.000đ | 1 module; RSCH-20261101-0009 [U4](https://icdayroi.com/txs0108e-8-kenh-chuyen-muc-logic-1-8v-3-3v-5v) |
| U5: DHT11 rời 4 chân | 1 | 25.000đ | 25.000đ | 1 cảm biến; RSCH-20261101-0009 [U5](https://chotroihn.vn/cam-bien-nhiet-do-do-am-dht11) |
| U6: OLED SSD1315 0,96 inch | 1 | 65.000đ | 65.000đ | 1 màn hình; RSCH-20261101-0009 [U6](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c) |
| Y1: Thạch anh 20MHz HC49 DIP | 1 | 1.500đ | 1.500đ | 1 thạch anh; RSCH-20261101-0010 [Y1](https://icdayroi.com/thach-anh-20mhz-hc49-dip) |
| R1,R3: Điện trở 10kΩ 1/4W 1% | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 2; trang báo hết hàng biến thể này; cần xác nhận nguồn khác [R1,R3](https://chotroihn.vn/tro-vach-1-4w-1-50c) |
| R2: Điện trở 4,7kΩ 1/4W 1% | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1 [R2](https://chotroihn.vn/tro-vach-1-4w-1-50c) |
| R4: Điện trở 100kΩ 1/4W 1% | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1; trang báo hết hàng biến thể này; cần xác nhận nguồn khác [R4](https://chotroihn.vn/tro-vach-1-4w-1-50c) |
| R10: Điện trở 1kΩ 1/4W 1% | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1 [R10](https://chotroihn.vn/tro-vach-1-4w-1-50c) |
| C1,C2,C3,C5,C6,C12,C13: Tụ gốm 100nF | 7 | 500đ | 3.500đ | Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua [C1,C2,C3,C5,C6,C12,C13](https://chotroihn.vn/tu-gom-vang-50v) |
| C7: Tụ hóa 470uF 10V | 1 | 1.000đ | 1.000đ | 1 tụ [C7](https://chotroihn.vn/tu-hoa-10v) |
| C8,C11: Tụ hóa 10uF 16V | 2 | 1.000đ | 2.000đ | 2 tụ; điện áp cao hơn tối thiểu 10V của BOM [C8,C11](https://chotroihn.vn/tu-hoa-16v) |
| C9,C10: Tụ gốm 22pF | 2 | 500đ | 1.000đ | Giá biến thể 22P; xác nhận C0G/NP0 và tải thạch anh trước khi mua [C9,C10](https://chotroihn.vn/tu-gom-vang-50v) |
| D1: LED xanh lá 3mm | 1 | 29.000đ | 29.000đ | Mua gói 100, dùng 1 [D1](https://chotroihn.vn/goi-100-con-led-duc-3mm) |
| F1: Cầu chì PTC radial Ihold 1A | 1 | Chưa xác nhận | Chưa cộng | Chưa có giá hợp lệ đúng quy cách. Không dùng giá giữ chỗ 0/1đ hoặc thay bằng SMD1.1A trong tổng |
| SW1,SW2: Nút nhấn 6x6 | 1 | 5.000đ | 5.000đ | Mua gói 10, dùng 2 [SW1,SW2](https://chotroihn.vn/bo-10-nut-nhan-4-chan) |
| J1: Terminal KF301 2 chân | 1 | 1.500đ | 1.500đ | 1 terminal [J1](https://chotroihn.vn/terminal-kf301-300v-15a) |
| J2A,J2B,J4,J5A,J5B: Header cái 2,54mm | 2 | 2.000đ | 4.000đ | 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt [J2A,J2B,J4,J5A,J5B](https://chotroihn.vn/jump-cai-don-1-40p-2-54) |
| J3: Header đực 2,54mm | 1 | 2.000đ | 2.000đ | 1 thanh 40 chân, dùng 6 chân ICSP; giả định chân đực module đi kèm module [J3](https://chotroihn.vn/jump-duc-don-1x40p-2-54) |
| SK1: Đế IC 40 chân | 1 | 1.500đ | 1.500đ | Biến thể 40 chân; xác nhận loại rộng cho PIC DIP40 [SK1](https://chotroihn.vn/de-ic) |
| TP1,TP2,TP3: Test point tự làm | 0 | 0đ | 0đ | Tận dụng chân/dây cắt thừa của header đã tính; không mua thêm |
| PCB: In PCB theo giá người dùng | 1 | 120.000đ | 120.000đ | Giá người dùng cung cấp, không phải giá nhà sản xuất đã khảo sát |

## Điểm cần chốt trước khi mua

- F1 vẫn là PTC radial 1A trong BOM. Chưa tìm được giá hợp lệ đúng quy cách; giá 0/1đ ở một số trang là giữ chỗ, không được cộng như linh kiện miễn phí. Tổng cuối = 505.000đ + giá F1 + các khoản phát sinh thực tế.
- Biến thể trở 10kΩ và 100kΩ ở nguồn tham khảo đang hết hàng; giá 6.000đ/gói vẫn được giữ như giá tham khảo, cần hỏi shop khác. Không thay điện trở kéo OE bằng giá trị khác chỉ vì còn hàng.
- Giá tụ gốm phổ thông chưa xác nhận điện môi X7R/C0G; đối chiếu đúng loại của BOM, có thể thay đổi giá khi chốt mua.
- Chưa gồm phí vận chuyển, adapter 5V/2A, cáp USB, vỏ, thiếc/flux và công hàn. Burn-E đã có nên không mua lại. Nếu module không đi kèm chân đực, bổ sung vật tư tương ứng.
- Giá tham khảo được đối chiếu: PIC có nguồn khác 145.000đ; SuperMini có nguồn khác 85.000đ; TXS có nguồn khác 18.000đ nhưng báo hết hàng. Không coi các mức đó là giá của shop đã chọn.

Nguồn/ledger: các IC/module chính RSCH-20261101-0009; linh kiện nhỏ/đầu nối RSCH-20261101-0010. PCB 120.000đ là thông tin người dùng.
