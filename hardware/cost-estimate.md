# Dự toán mua linh kiện và in PCB — 1 bộ

Sinh tự động từ `cost-estimate.csv` bởi `hardware/generate.py`; danh sách lắp đầy đủ ở [BOM.md](BOM.md). Giá tham khảo ngày **01/11/2026**, đơn vị VND; ledger RSCH-20261101-0009/0010/0011. PCB 120.000đ do người dùng cung cấp.

- Linh kiện dùng trên một mạch (phân bổ theo số lượng lắp): **217.140đ**, chưa gồm mục chưa có giá.

## Tiền mua thực tế theo gói/thanh

| Mục | Số đơn vị/gói mua | Giá mỗi đơn vị/gói | Thành tiền mua | Quy cách / ghi chú |
|---|---:|---:|---:|---|
| [U1: AT89S52 DIP-40](https://chotroihn.vn/at89s52-24pu-dip40) | 1 | 27.000đ | 27.000đ | 1 IC DIP40; RSCH-20261101-0011; shop khác có giá 79.000đ |
| [U2: ESP32-C3 SuperMini 4MB](https://icdayroi.com/kit-phat-trien-wifi-bluetooth-esp32-c3-super-mini-4mb) | 1 | 75.000đ | 75.000đ | 1 board; RSCH-20261101-0009 |
| [U4: Module TXS0108E](https://icdayroi.com/txs0108e-8-kenh-chuyen-muc-logic-1-8v-3-3v-5v) | 1 | 15.000đ | 15.000đ | 1 module; RSCH-20261101-0009 |
| [U5: DHT11 rời 4 chân](https://chotroihn.vn/cam-bien-nhiet-do-do-am-dht11) | 1 | 25.000đ | 25.000đ | 1 cảm biến; RSCH-20261101-0009 |
| [U6: OLED SSD1315 0,96 inch](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c) | 1 | 65.000đ | 65.000đ | 1 màn hình; RSCH-20261101-0009 |
| [Y1: Thạch anh 11.0592MHz HC49 DIP](https://icdayroi.com/thach-anh-11-0592mhz-hc49-dip) | 1 | 1.500đ | 1.500đ | 1 thạch anh; RSCH-20261101-0011 |
| [R1,R3,R7,R8,R9: Điện trở 10kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 5; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| [R2: Điện trở 4,7kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1 |
| [R4: Điện trở 100kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| R5: Điện trở 4.7kΩ 1/4W | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá; có thể lấy từ gói 4 |
| [C1,C16: Tụ gốm 100nF](https://chotroihn.vn/tu-gom-vang-50v) | 2 | 500đ | 1.000đ | Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| [C2: Tụ hóa 10uF 16V](https://chotroihn.vn/tu-hoa-16v) | 1 | 1.000đ | 1.000đ | C2 reset; kiểm tra cực tính |
| [C9,C10: Tụ gốm 22pF](https://chotroihn.vn/tu-gom-vang-50v) | 2 | 500đ | 1.000đ | Giá biến thể 22P; xác nhận C0G/NP0 và tải thạch anh trước khi mua |
| U7: LM7805 TO-220 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| D2: Diode Schottky SR360 DO-201AD | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| D3: Diode 1N4007 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| Q1: Transistor 2SC1815-GR TO-92 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| R6: Điện trở 2.2kΩ 1/4W | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| U8: Opto PC817 DIP-4 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| C14: Tụ hóa 100uF 25V | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| [SW1,SW2: Nút nhấn 6x6](https://chotroihn.vn/bo-10-nut-nhan-4-chan) | 1 | 5.000đ | 5.000đ | Mua gói 10, dùng 2 |
| J1: Jack DC 5.5x2.1 hàn mạch | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| J7: Domino 2 chân 5.08mm | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| [J2A,J2B,J4,J5A,J5B: Header cái 2,54mm](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 2 | 2.000đ | 4.000đ | 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| [J3: Header đực 2,54mm](https://chotroihn.vn/jump-duc-don-1x40p-2-54) | 1 | 2.000đ | 2.000đ | 1 thanh 40 chân, dùng 6 chân ISP AT89S52; giả định chân đực module đi kèm module |
| K1: Relay SRD-12VDC-SL-C | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| J6: Domino 2 chân 5.08mm | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| [SK1: Đế IC 40 chân](https://chotroihn.vn/de-ic) | 1 | 1.500đ | 1.500đ | Biến thể 40 chân; xác nhận loại rộng cho AT89S52 DIP40 |
| TP1,TP2,TP3: Test point tự làm | 0 | 0đ | 0đ | Tận dụng chân/dây cắt thừa của header đã tính; không mua thêm |
| PCB: In PCB theo giá người dùng | 1 | 120.000đ | 120.000đ | Giá người dùng cung cấp, không phải giá nhà sản xuất đã khảo sát |

- Linh kiện mua mới theo gói/thanh: **242.000đ**, chưa gồm mục chưa có giá.
- In PCB theo giá người dùng: **120.000đ**.
- **Tổng tiền mua + PCB: 362.000đ, chưa gồm mục chưa có giá.**
- Nếu chỉ phân bổ lượng linh kiện dùng trên một PCB: **337.140đ**, chưa gồm mục chưa có giá. Phần chênh lệch là linh kiện dư từ gói/thanh mua.
- J1, J6, J7, U7, D2, D3, Q1, R5, R6, U8, C14 và K1 chưa khảo sát giá, để trống trong CSV; không tính thành 0đ. Giá tụ tham khảo cần xác nhận đúng điện môi; trở 10kΩ/100kΩ ở nguồn giá đang báo hết hàng.
- Chưa gồm vận chuyển, adapter/cáp, vỏ, thiếc/flux và công hàn. Burn-E đã có nên không mua lại.
