# Kịch bản thuyết trình — Đồ án 2 (v1.1.0)

Bộ slide: https://claude.ai/artifact/ES5pMxzQYagHhdiFTj7gnK

## Slide 1. Thiết kế hệ thống giám sát nhiệt độ, độ ẩm sử dụng AT89S52, ESP32-C3 và nền tảng IoT

Kính chào thầy và các bạn. Nhóm em trình bày đề tài thiết kế hệ thống giám sát nhiệt độ, độ ẩm dùng AT89S52, ESP32-C3 và nền tảng IoT ThingsBoard. Hệ thống đo và hiển thị tại chỗ, gửi dữ liệu lên Internet, và điều khiển relay theo nhiệt độ.

## Slide 2. Đặt vấn đề và mục tiêu

Nhiệt ẩm kế thông thường chỉ xem tại chỗ, không lưu lịch sử và không cảnh báo. Đề tài giữ phần đo trên AT89S52 và thêm ESP32-C3 để đưa dữ liệu lên Internet. Sáu mục tiêu gồm: đo và hiển thị, giao tiếp hai mức điện áp, kết nối Internet, dashboard, relay theo nhiệt độ và thiết kế mạch in.

## Slide 3. Sơ đồ khối hệ thống

Hệ thống chia ba lớp. AT89S52 lo phần tại chỗ: đo, hiển thị, relay. ESP32-C3 lo kết nối mạng. ThingsBoard lo lưu trữ và cảnh báo. TXS0108E nằm giữa để chuyển mức 5 V và 3,3 V. Nhờ tách vai trò, mất mạng không ảnh hưởng chức năng tại chỗ.

## Slide 4. Khối nguồn 12 V → 5 V → 3,3 V

Nguồn 12 V vào qua jack hoặc domino, qua diode Schottky SR360 chống cắm ngược. LM7805 tạo 5 V, ESP32 tạo 3,3 V. Dòng tải và công suất là số ước tính, chưa đo. Relay lấy thẳng 12 V để không tải lên LM7805. Đường 12 V rộng 2 mm, nguồn 1 mm, tín hiệu 0,5 mm.

## Slide 5. AT89S52 và ngoại vi

Bảng phân bổ chân AT89S52. I²C làm bằng phần mềm trên P0.3, P0.4, hai chân nằm ngay dưới module chuyển mức; vì P0 là cực máng hở nên có R8, R9 kéo lên 5 V; UART dùng P3.0, P3.1; DHT11 ở P3.2; nút trang P3.3; relay ở P2.0. Thạch anh 11,0592 MHz cho tốc độ 9600 baud chính xác. Reset mức cao bằng tụ và điện trở.

## Slide 6. Chuyển mức TXS0108E và ESP32-C3

AT89S52 chạy 5 V, ESP32 và OLED chạy 3,3 V, nên dùng TXS0108E chuyển mức hai chiều. Bốn kênh dùng cho UART và I²C. Kênh và chân được chọn theo vị trí trên mạch in để dây đi thẳng. Phía 5 V của I²C có R8, R9 kéo lên vì cổng P0 là cực máng hở. Chân OE được kéo xuống bằng R4 và chỉ bật sau khi nguồn hai phía ổn định.

## Slide 7. Khối relay cách ly quang

Relay điều khiển qua opto PC817. Phía LED dùng 5 V, phía relay dùng 12 V, chung GND nên đây là tách nguồn. Q1 C1815 khuếch đại dòng cho cuộn. Tải nối COM và NO, có điện khi nhiệt độ từ 32 độ trở lên, tắt khi về 30 độ. Sau reset và khi cảm biến lỗi relay luôn tắt. Các dòng là số tính toán.

## Slide 8. Sơ đồ nguyên lý và mạch in

Sơ đồ nguyên lý vẽ trên KiCad 10, chia thành chín khối theo chức năng, trong khối nối dây, giữa các khối nối bằng nhãn; kiểm tra luật điện không lỗi. Mạch in hai lớp 92,5 nhân 84,7 mm đã đi dây đủ, đường mạch chỉ đi thẳng hoặc chéo 45 độ, kiểm tra DRC không còn lỗi điện, GND phủ đồng cả hai mặt. Chi phí linh kiện đã có giá là 217 nghìn, in PCB 120 nghìn; một số linh kiện chưa khảo sát giá.

## Slide 9. Phần mềm và giao thức

Hai vi điều khiển trao đổi ba loại khung văn bản có CRC-8. AT89S52 gửi khung M chứa số đo; ESP32 gửi khung S báo trạng thái mạng và khung T chứa giờ. Firmware AT89S52 viết bằng C và hợp ngữ, chiếm khoảng 7,4 KB. ESP32 gửi HTTPS mỗi 10 giây. Dashboard có 12 widget.

## Slide 10. Kiểm thử, kết luận và hướng phát triển

Phần đã đạt: sơ đồ nguyên lý không lỗi, các kiểm thử phần mềm đạt, firmware ESP32 build được. Mạch thật chưa chế tạo; nhóm đã chuẩn bị 16 kịch bản kiểm thử. Hướng phát triển: cảm biến chính xác hơn, lưu bù dữ liệu, chỉnh ngưỡng từ xa, nguồn xung. Em xin cảm ơn thầy và các bạn.
