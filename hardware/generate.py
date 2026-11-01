"""One hardware source for the purchasing BOM and labelled wiring overview."""
import csv
import html
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PARTS=[
('U1',1,'PIC16F877A-I/P','DIP-40','Bộ xử lý đo/hiển thị; nguồn 5 V'),
('U2',1,'ESP32 DevKit V1 / ESP32-WROOM-32','30 chân, 2 hàng 1x15','Không dùng WROVER/PSRAM hoặc S3 thay trực tiếp; chọn đúng board trước khi làm PCB'),
('U3',1,'DS1307+','DIP-8','RTC rời; không dùng module sạc pin'),
('U4',1,'SN74AHCT125N','DIP-14','Chuyển UART ESP32 TX 3,3 V lên PIC RX 5 V; không thay bằng 74HC125'),
('U5',1,'DHT11 cảm biến rời','4 chân','VCC/DATA/NC/GND; không nhầm pin module 3 chân'),
('U6',1,'OLED trắng 0,96 inch SSD1315 I²C 128x64','Module 4 chân','Module Hshop đã chọn; cấp 3,3 V, kiểm tra thứ tự chân in trên module'),
('Q1,Q2',2,'BSS138','SOT-23','Chuyển mức hai chiều SDA/SCL: G=3V3, S=LV, D=HV'),
('Y1',1,'Thạch anh 20 MHz','HC-49S','Dao động PIC; chọn loại phù hợp HS, đối chiếu điện dung tải'),
('Y2',1,'Thạch anh 32,768 kHz CL=12,5 pF','Dạng trụ 2 chân','RTC; không lắp tụ tải ngoài cho DS1307'),
('R1,R3',2,'10 kΩ 1% 0,25 W','Axial THT','R1 kéo MCLR lên 5 V; R3 kéo nút trang lên 5 V'),
('R2',1,'4,7 kΩ 1% 0,25 W','Axial THT','Kéo DATA DHT11 lên 5 V'),
('R4',1,'10 kΩ 1% 0,25 W','Axial THT','Nhánh trên chia áp PIC TX → ESP32 RX'),
('R5',1,'20 kΩ 1% 0,25 W','Axial THT','Nhánh dưới chia áp UART xuống GND'),
('R6,R7,R8,R9',4,'4,7 kΩ 1% 0,25 W','Axial THT','SDA/SCL: hai kéo lên 5 V và hai kéo lên 3,3 V; không nhân đôi pull-up nếu module đã có'),
('R10',1,'1 kΩ 0,25 W','Axial THT','Hạn dòng LED nguồn'),
('C1,C2,C3,C4,C5,C6',6,'100 nF X7R ≥16 V','THT 2,54 mm','Hai cặp VDD PIC, U4, U3, OLED 3V3, ESP32 5V; đặt sát tải'),
('C7',1,'470 µF ≥10 V','Tụ hóa radial','Tụ nguồn 5 V gần ESP32; đúng cực'),
('C8',1,'10 µF ≥10 V','Tụ hóa radial','Lọc nhánh 3,3 V OLED; đúng cực'),
('C9,C10',2,'22 pF C0G/NP0 ≥25 V','Tụ gốm THT','Hai tụ Y1; giá trị khởi đầu, đối chiếu CL thạch anh trước khi chốt PCB'),
('C11',1,'10 µF ≥10 V','Tụ hóa radial','Lọc nhánh 5 V PIC/RTC; đúng cực'),
('C12',1,'100 nF X7R ≥16 V','THT 2,54 mm','Lọc nguồn sát VCC/GND DHT11'),
('D1',1,'LED xanh 3 mm','THT','LED báo có nguồn 5 V'),
('F1',1,'Cầu chì tự phục hồi Ihold 1 A ≥6 V','Radial THT','Mắc nối tiếp đầu vào 5 V; đối chiếu dòng khởi động thực tế'),
('SW1,SW2',2,'Nút nhấn thường hở','Tactile 6x6 mm','SW1 đổi trang; SW2 reset PIC'),
('BH1',1,'Đế CR2032 không mạch sạc','THT','Hàn đế; không hàn trực tiếp vào viên pin'),
('J1',1,'Terminal cấp nguồn 2 chân','Pitch 5,08 mm','Đầu vào 5 V và GND; ghi rõ cực tính'),
('J2A,J2B',2,'Header cái 1x15','Pitch 2,54 mm','Đế cắm ESP32; đo khoảng cách hai hàng của board thực tế'),
('J4',1,'Header cái 1x4','Pitch 2,54 mm','Đế cắm OLED'),
('J3',1,'Header đực ICSP 1x6','Pitch 2,54 mm','VPP/VDD/GND/PGD/PGC/NC'),
('SK1',1,'Đế IC DIP-40','Wide 15,24 mm','Đế PIC, hàn đế rồi cắm IC'),
('SK2',1,'Đế IC DIP-8','Pitch 2,54 mm','Đế DS1307'),
('SK3',1,'Đế IC DIP-14','Pitch 2,54 mm','Đế SN74AHCT125'),
('TP1,TP2,TP3',3,'Test point vòng dây','THT','Đo 5 V / 3,3 V / GND')
]

def main():
    with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f); writer.writerow(['Reference','Quantity','Component','Package','Assembly note']); writer.writerows(PARTS)
    lines=['# Danh sách đầy đủ linh kiện trên mạch','',
        'Phương án lắp: PIC, DS1307 và AHCT125 dùng IC rời có đế; ESP32 và OLED là module cắm header. Mọi đế/header trong bảng đều được hàn lên PCB. IC/module cắm vào sau khi kiểm tra nguồn. Không cộng lại những linh kiện đã có sẵn bên trong module.', '',
        '| Ký hiệu | SL | Linh kiện | Kiểu lắp | Vị trí / lưu ý |','|---|---:|---|---|---|']
    lines += [f'| {r} | {n} | {part} | {pkg} | {note} |' for r,n,part,pkg,note in PARTS]
    lines += ['',f'**Tổng số chi tiết trong bảng:** {sum(p[1] for p in PARTS)} (bao gồm IC/module/đế; không gồm PCB và vật tư ngoài mạch).',
        '', '## Vật tư đi kèm, không hàn trực tiếp', '',
        '- 1 pin CR2032 3 V dùng với BH1; tuyệt đối không dùng mạch sạc cho pin CR2032.',
        '- 1 adapter DC 5 V / 2 A ổn áp, dây cấp nguồn và dây USB lập trình ESP32.',
        '- 1 PCB theo kích thước thực tế ESP32/OLED; thiếc, flux và dây nối cho bản thử.',
        '- PICkit tương thích PIC16F877A và MPLAB XC8 để nạp/debug PIC; đây là dụng cụ dùng lại.',
        '', '## Điều kiện mua/lắp', '',
        '- BOM không có giá vì chưa khảo sát giá mua. Không đặt PCB chỉ dựa vào sơ đồ luồng: cần schematic/netlist và kiểm tra footprint.',
        '- Nếu OLED đã có pull-up SDA/SCL lên VCC 3,3 V thì bỏ R8/R9 tương ứng, ghi DNP; vẫn giữ vị trí trên PCB.',
        '- Nếu mua board BSS138 chuyển mức hoàn chỉnh thay Q1/Q2, các điện trở kéo thường có sẵn: đối chiếu rồi bỏ linh kiện trùng. Không lắp cả hai phương án cùng lúc.',
        '- Chọn ESP32 module đã hàn chân đực. Nếu hàng mua chưa có chân, bổ sung 2 thanh header đực 1x15; không tính trùng với header có sẵn.',
        '- Chỉ dùng một nguồn cấp 5 V: tháo nguồn ngoài khi cắm USB nếu board không có bảo vệ chống cấp ngược. Không nối adapter vào chân 3V3.',
        '- Giá trị/điện áp từng linh kiện là cấu hình thiết kế; xác minh nguồn và dạng sóng trên mạch thật trước khi vận hành.', '']
    (ROOT/'BOM.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'BOM: {len(PARTS)} rows, {sum(p[1] for p in PARTS)} parts')

if __name__=='__main__': main()
