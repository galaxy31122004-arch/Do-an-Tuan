"""One hardware source for the purchasing BOM and labelled wiring overview."""
import csv
import html
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PARTS=[
('U1',1,'PIC16F877A-I/P','DIP-40','Bộ xử lý đo/hiển thị; nguồn 5 V'),
('U2',1,'ESP32-C3 SuperMini','16 chân, 2 hàng 1x8','Board ESP32-C3 SuperMini; xác minh footprint và nhãn GPIO trước khi làm PCB'),
('U4',1,'Module TXS0108E 8 kênh','Module 2 hàng, đối chiếu footprint','A=3,3 V; B=5 V; bốn kênh I²C/UART; OE từ ESP32 GPIO6'),
('U5',1,'DHT11 cảm biến rời','4 chân','VCC/DATA/NC/GND; không nhầm pin module 3 chân'),
('U6',1,'OLED trắng 0,96 inch SSD1315 I²C 128x64','Module 4 chân','Module Hshop đã chọn; cấp 3,3 V, kiểm tra thứ tự chân in trên module'),
('Y1',1,'Thạch anh 20 MHz','HC-49S','Dao động PIC; chọn loại phù hợp HS, đối chiếu điện dung tải'),
('R1,R3',2,'10 kΩ 1% 0,25 W','Axial THT','R1 kéo MCLR lên 5 V; R3 kéo nút trang lên 5 V'),
('R2',1,'4,7 kΩ 1% 0,25 W','Axial THT','Kéo DATA DHT11 lên 5 V'),
('R4',1,'100 kΩ 1% 0,25 W','Axial THT','Kéo OE TXS0108E xuống GND khi ESP32 khởi động; bỏ pull-up OE trên module nếu có'),
('R10',1,'1 kΩ 0,25 W','Axial THT','Hạn dòng LED nguồn'),
('C1,C2,C3,C5,C6',5,'100 nF X7R ≥16 V','THT 2,54 mm','Hai cặp VDD PIC, TXS VCCB 5V, OLED 3V3, ESP32 5V; đặt sát tải'),
('C7',1,'470 µF ≥10 V','Tụ hóa radial','Tụ nguồn 5 V gần ESP32; đúng cực'),
('C8',1,'10 µF ≥10 V','Tụ hóa radial','Lọc nhánh 3,3 V OLED; đúng cực'),
('C9,C10',2,'22 pF C0G/NP0 ≥25 V','Tụ gốm THT','Hai tụ Y1; giá trị khởi đầu, đối chiếu CL thạch anh trước khi chốt PCB'),
('C11',1,'10 µF ≥10 V','Tụ hóa radial','Lọc nhánh 5 V PIC; đúng cực'),
('C12',1,'100 nF X7R ≥16 V','THT 2,54 mm','Lọc nguồn sát VCC/GND DHT11'),
('C13',1,'100 nF X7R ≥16 V','THT 2,54 mm','Lọc VCCA 3,3 V của TXS0108E sát module'),
('D1',1,'LED xanh 3 mm','THT','LED báo có nguồn 5 V'),
('F1',1,'Cầu chì tự phục hồi Ihold 1 A ≥6 V','Radial THT','Mắc nối tiếp đầu vào 5 V; đối chiếu dòng khởi động thực tế'),
('SW1,SW2',2,'Nút nhấn thường hở','Tactile 6x6 mm','SW1 đổi trang; SW2 reset PIC'),
('J1',1,'Terminal cấp nguồn 2 chân','Pitch 5,08 mm','Đầu vào 5 V và GND; ghi rõ cực tính'),
('J2A,J2B',2,'Header cái 1x8','Pitch 2,54 mm','Đế cắm ESP32; đo khoảng cách hai hàng của board thực tế'),
('J4',1,'Header cái 1x4','Pitch 2,54 mm','Đế cắm OLED'),
('J3',1,'Header dịch vụ ICSP 1x6','Pitch 2,54 mm','VPP/VDD/GND/PGD/PGC/NC; nạp chính bằng Burn-E ngoài mạch'),
('J5A,J5B',2,'Header cái 1x10 cho module TXS0108E','Pitch 2,54 mm, xác minh hàng mua','Hàn đế module; chỉnh số chân/footprint nếu module thực tế khác'),
('SK1',1,'Đế IC DIP-40','Wide 15,24 mm','Đế PIC, hàn đế rồi cắm IC'),
('TP1,TP2,TP3',3,'Test point vòng dây','THT','Đo 5 V / 3,3 V / GND')
]

def main():
    with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f); writer.writerow(['Reference','Quantity','Component','Package','Assembly note']); writer.writerows(PARTS)
    lines=['# Danh sách đầy đủ linh kiện trên mạch','',
        'Phương án lắp: PIC dùng IC rời có đế; ESP32, OLED và TXS0108E là module cắm header. Mọi đế/header trong bảng đều được hàn lên PCB. IC/module cắm vào sau khi kiểm tra nguồn. Không cộng lại những linh kiện đã có sẵn bên trong module.', '',
        '| Ký hiệu | SL | Linh kiện | Kiểu lắp | Vị trí / lưu ý |','|---|---:|---|---|---|']
    lines += [f'| {r} | {n} | {part} | {pkg} | {note} |' for r,n,part,pkg,note in PARTS]
    lines += ['',f'**Tổng số chi tiết trong bảng:** {sum(p[1] for p in PARTS)} (bao gồm IC/module/đế; không gồm PCB và vật tư ngoài mạch).',
        '', '## Vật tư đi kèm, không hàn trực tiếp', '',
        '- 1 adapter DC 5 V / 2 A ổn áp, dây cấp nguồn và dây USB lập trình ESP32.',
        '- 1 PCB theo kích thước thực tế ESP32/OLED; thiếc, flux và dây nối cho bản thử.',
        '- Mạch nạp Burn-E đang sử dụng, cáp USB và phần mềm đúng phiên bản để nạp/verify HEX PIC16F877A; đây là dụng cụ dùng lại, không hàn lên mạch.',
        '', '## Điều kiện mua/lắp', '',
        '- BOM không có giá vì chưa khảo sát giá mua. Không đặt PCB chỉ dựa vào sơ đồ luồng: cần schematic/netlist và kiểm tra footprint.',
        '- TXS0108E có pull-up nội. Không lắp thêm bốn điện trở 4,7 kΩ kéo bus như thiết kế cũ; kiểm tra pull-up có sẵn trên OLED/module và đo dạng sóng.',
        '- OE nối GPIO6 và R4 100 kΩ xuống GND; không để module kéo cứng OE lên nguồn. Phải kiểm tra/tháo cầu nối hoặc pull-up OE nếu module đã gắn.',
        '- Chọn ESP32-C3 SuperMini đã hàn chân đực. Nếu hàng mua chưa có chân, bổ sung 2 thanh header đực 1x8; không tính trùng với header có sẵn.',
        '- Chỉ dùng một nguồn cấp 5 V: tháo nguồn ngoài khi cắm USB nếu board không có bảo vệ chống cấp ngược. Không nối adapter vào chân 3V3.',
        '- Giá trị/điện áp từng linh kiện là cấu hình thiết kế; xác minh nguồn và dạng sóng trên mạch thật trước khi vận hành.', '']
    (ROOT/'BOM.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'BOM: {len(PARTS)} rows, {sum(p[1] for p in PARTS)} parts')

if __name__=='__main__': main()
