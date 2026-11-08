# Yêu cầu thông tin và độ sâu — Báo cáo Đồ án 2

Mức viết: `khái quát` · `vừa đủ` · `chuyên sâu` · `tùy chỉnh`. Mức đề xuất ghi trong ngoặc, chờ người dùng chốt.

| Phần | Mức (đề xuất) | Dữ liệu đã có | Còn thiếu | Trạng thái |
|---|---|---|---|---|
| Mở đầu | vừa đủ | Bản tóm tắt đề tài | — | chờ duyệt |
| Chương 1 | vừa đủ | Datasheet công khai, docs/sources.md | Có giới hạn trang cho chương lý thuyết không | chờ duyệt |
| Chương 2 | chuyên sâu | KiCad, BOM, wiring.md, net class | PCB chưa đi dây xong; kích thước header ESP32/TXS chưa đo; giá một số linh kiện chưa khảo sát | chờ duyệt |
| Chương 3 | chuyên sâu | firmware v0.2.0, dashboard/generate.py | Ảnh dashboard chạy thật (nếu có) | chờ duyệt |
| Chương 4 | vừa đủ | Kế hoạch kiểm thử, kiểm thử phần mềm (checksum HEX, artifact) | **Ảnh mạch thật, số đo nhiệt độ/độ ẩm, kết quả gửi cloud** — chưa có, không tự tạo | chờ dữ liệu |
| Kết luận | khái quát | — | Phụ thuộc chương 4 | chờ |

## Đã chốt (2026-11-08)
- MSSV, địa danh/năm trên bìa: để trống, người dùng tự điền.
- Bìa ghi "BÁO CÁO ĐỒ ÁN 2"; bìa không ảnh (khung, logo, chữ).
- Khoa không quy định thêm; dùng định dạng mặc định trong tệp 01.
- Đồng ý mức viết từng chương như bảng.
- Mạch thật chưa làm/đo: chương 4 viết dạng kế hoạch kiểm thử, kết quả bổ sung sau.
- Không có lời cảm ơn.
- Dàn ý tệp 01 đã duyệt. Tiến độ: Mở đầu, Chương 1, 2 đã duyệt; Chương 3, 4, Kết luận, TLTK, Phụ lục viết theo yêu cầu "viết hết" và dựng Word `drafts/bao-cao-do-an-2.docx`, chờ duyệt.

## Câu hỏi ưu tiên (đã trả lời)
1. Mã số sinh viên của hai bạn; năm và địa danh ghi trên bìa (ví dụ "Bình Định, 2026"?).
2. Loại tài liệu ghi trên bìa: "BÁO CÁO ĐỒ ÁN 2" hay tên khác theo khoa?
3. Khoa có quy định số trang, cỡ chữ, lề hay cách trích dẫn (IEEE/APA) không?
4. Mức viết từng chương như bảng trên có đồng ý không?
5. Chương 4: mạch thật đã làm/đo chưa? Nếu chưa, viết chương 4 dạng kế hoạch kiểm thử và để kết quả bổ sung sau.
6. Bìa không ảnh (chỉ khung, logo, chữ) có được không?
7. Có cần lời cảm ơn, nhận xét GVHD không?

## Ghi chú
- Không suy diễn kết quả đo hay độ chính xác chưa kiểm chứng.
- Thiết kế đã thay đổi so với bản tóm tắt: thêm relay (PC817 + C1815, bật ≥ 32 °C, tắt ≤ 30 °C), nguồn 12 V qua LM7805, OE = GPIO0, TX ESP32 = GPIO3.
