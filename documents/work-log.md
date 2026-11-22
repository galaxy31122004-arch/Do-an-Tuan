# Nhật ký công việc

## 2026-11-22 09:20 — Rà soát và sửa các tồn đọng PCB, firmware, báo cáo, slide

- Yêu cầu: kiểm tra vấn đề còn lại, sau đó sửa toàn bộ.
- PCB: ngắt viền in lụa U4 tại pad R8 (`sandbox/kicad/fix_u4_silk.py`). KiCad không chạy khi ghi file.
- Xuất: PDF sơ đồ nguyên lý, hình PCB, gói Gerber và file khoan tại `versions/pcb/env-monitor/v1.0.0/` (`sandbox/kicad/export_release.py`).
- Firmware ESP32 v0.2.0: chuyển sang module Wi-Fi nhiều mạng `wifi_nvs`, sinh `wifi_secrets.h` (gitignored), bỏ thông tin Wi-Fi khỏi `secrets.h`.
- Tài liệu: sửa via, DRC, Wi-Fi, trạng thái kiểm chứng trong `hardware/wiring.md`, `docs/`, README và chương 2, 3, 4 của báo cáo.
- Báo cáo: build lại bản nháp DOCX và PDF, 41 trang. Chưa đánh phiên bản, chờ người dùng duyệt.
- Slide: đồng bộ bản claude.ai lên version 9 (P1.0, GPIO10, tín hiệu 0,3 mm, hình mới). Chưa tạo bản giao PPTX.
- Kết quả: ERC 0 lỗi; DRC 0 lỗi, 0 cảnh báo, 0 chân chưa nối, 0 sai khác với sơ đồ. `tests/check_artifacts.py` PASS. PlatformIO `esp32c3` và `demo` build thành công.
- Chưa kiểm chứng: mạch thật, Wi-Fi trên ESP32 thật, gửi ThingsBoard thật, Gerber trên công cụ của nhà in.
- Điểm mở: chưa có `secrets.h` thật (host, token, root CA); không có mạng Wi-Fi 2,4 GHz đã lưu nào trong vùng phủ lúc build; chưa commit.

## 2026-11-22 11:10 — Mở KiCad để duyệt mạch, kiểm tra gói Gerber

- Yêu cầu: mở lại mạch để duyệt và xuất Gerber.
- Mở `hardware/pcb/env-monitor.kicad_pro` bằng KiCad 10.0.
- Không xuất lại: `env-monitor-gerber_v1.0.0.zip` (09:17) mới hơn `env-monitor.kicad_pcb` (09:15), bản đã giao không ghi đè.
- Gói có 10 file: F/B Cu, F/B Mask, F/B Silkscreen, Edge Cuts, file khoan, bản đồ khoan, job.
- Chưa kiểm chứng: người dùng chưa duyệt xong mạch, Gerber chưa xem trên công cụ của nhà in.
- Nếu người dùng lưu thay đổi trên PCB, phải xuất phiên bản mới v1.0.1.

## 2026-11-22 11:58 — Xuất Gerber PCB v1.0.1 sau khi người dùng sửa mạch

- Yêu cầu: kiểm tra lại mạch và xuất Gerber.
- Người dùng dời R8, R9 và xóa hai đoạn dây thừa (SDA5, RELAY) trong KiCad, bản lưu 11:57.
- Chạy `sandbox/kicad/export_release.py 1.0.1`. Lần chạy trước bị chặn do còn dây RELAY cụt.
- Kết quả: ERC 0 lỗi; DRC 0 lỗi, 0 cảnh báo, 0 chân chưa nối, 0 sai khác với sơ đồ.
- Xuất: `versions/pcb/env-monitor/v1.0.1/` (gói Gerber, file khoan, PDF sơ đồ). Cập nhật PDF sơ đồ và hình PCB trong `figures/`.
- Chưa kiểm chứng: Gerber trên công cụ của nhà in, mạch thật.
- Điểm mở: bản nháp báo cáo và slide chưa dựng lại với hình mới; dây tín hiệu SDA5, RELAY rộng 0,5 mm trong khi tài liệu ghi 0,3 mm; chưa commit.

## 2026-11-22 12:13 — Đồng bộ báo cáo và slide theo PCB v1.0.1

- Yêu cầu: cập nhật báo cáo và slide theo mạch v1.0.1, dây tín hiệu 0,5 mm.
- Đo trên `env-monitor.kicad_pcb`: tín hiệu 0,5 mm; +5V, +3V3, GND 1 mm; anode D3 1,5 mm; +12V và J6 2 mm; 0 via. Luật khoảng cách tối thiểu 0,5 mm.
- Sửa `hardware/wiring.md`, chương 2 và 4 của báo cáo, slide `nguon` và `kicad` (ảnh 3D mới).
- Báo cáo: build lại bản nháp DOCX và PDF, 41 trang; không còn 0,3 mm, 0,35 mm, 0,25 mm.
- Slide: đăng bản claude.ai version 10.
- `tests/check_artifacts.py` PASS.
- Chưa kiểm chứng: chưa xem lại bố cục slide sau khi đăng, Gerber trên công cụ của nhà in, mạch thật.
- Điểm mở: báo cáo và slide chưa đánh phiên bản, chờ người dùng duyệt; chưa commit.

## 2026-11-22 12:25 — Commit và push nhánh release/pcb-v1.0.1

- Yêu cầu: commit và push.
- Tạo nhánh `release/pcb-v1.0.1`, commit `e3dd015` (37 file), push lên `origin`. Nhánh gồm cả commit `4a8ccca` trước đó chưa push.
- Quét file đã stage: không có `wifi_secrets.h`, `secrets.h`, `.bin`, `.elf`; các mẫu mật khẩu, token chỉ là giá trị mẫu.
- Điểm mở: `main` chưa được merge; báo cáo và slide chưa đánh phiên bản.
