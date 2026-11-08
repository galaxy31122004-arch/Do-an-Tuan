# Do an 2 - Giam sat nhiet do do am qua Internet — hướng dẫn chung cho AI

`AGENTS.md` là nguồn quy tắc chung cho Codex và Claude. Codex đọc trực tiếp; `CLAUDE.md` dẫn về đây cho Claude. Khi đổi quy tắc, sửa file này. Không tạo hướng dẫn Gemini, Cursor hoặc Copilot.

## Bối cảnh

- Workspace: `D:\Randombullsheet\Do-an-Tuan`.
- Mục đích: Đồ án 2 — giám sát nhiệt độ/độ ẩm qua Internet. DHT11 → AT89S52 → OLED SSD1315; AT89S52 ↔ ESP32-C3 → Wi-Fi → ThingsBoard dashboard.
- Repo có sẵn trước khi áp cấu trúc này: code và tài nguyên đang duy trì nằm ở `firmware/`, `dashboard/`, `hardware/`, `tests/`, `docs/`; giữ nguyên các đường dẫn đó.
- Mạch PCB sẽ vẽ thủ công; không liên kết tới workspace KiCad bên ngoài.
- Trạng thái AXON ở `.planning/`. Thử nghiệm mới đặt ở `sandbox/`.

## Dự án liên kết

Chỉ ghi dự án, đường dẫn và quyền chỉnh sửa đã được người dùng xác nhận hoặc đã kiểm tra. Hiện chưa khai báo dự án liên kết trong mẫu này.

## Quy tắc làm việc

1. Đọc quy tắc tại thư mục con trước khi sửa phần tương ứng; giữ các lựa chọn đã được người dùng chốt.
2. Giữ project hoàn chỉnh và đường dẫn build. Khi tổ chức lại, cập nhật link/script và xác minh các entrypoint còn chạy.
3. Ảnh hoặc tài liệu có thông tin được lưu trong `documents/sources/<topic>/`; mỗi file có ghi chú `.md` cạnh nguồn, ghi nguồn gốc, yêu cầu, nội dung xác nhận và điểm chưa rõ.
4. Phân biệt dữ liệu thật, dữ liệu mẫu, mô phỏng và suy luận; không dùng ảnh để đoán thông số hoặc kết luận đã chạy phần cứng.
5. Giữ nguyên bản gốc và file người dùng chỉnh. Bản xuất mới không ghi đè bản review; mọi bản giao bắt buộc có phiên bản và lưu ở `versions/` (xem mục Phiên bản).
6. Ghi phương án chưa chốt vào `considerations/`. Không coi phương án là yêu cầu đã duyệt.
7. Báo kết quả dựa trên kiểm tra thực tế phù hợp; ghi rõ những phần chưa chạy. Tài liệu kiểm thử nằm ở `documents/verification/`.

## Phiên bản (bắt buộc)

Mọi sản phẩm giao trong workspace này đều phải có phiên bản `vX.Y.Z` và nằm trong thư mục mới `versions/<loại>/<tên>/v<X.Y.Z>/`; không có bản giao nào không đánh số, không sửa trong `versions/`, không ghi đè bản đã giao. Mọi skill cá nhân dùng trong workspace đều tuân theo cấu trúc này.

Workspace này không dùng thư mục `source-code/`. Code firmware đánh phiên bản theo mục Phiên bản firmware bên dưới. Không xác định được phiên bản trước thì hỏi, không đoán.

## Phiên bản tài liệu Word

Soạn trong `documents/<ten>/` (hai tệp kế hoạch, `figures/`, `drafts/`); đầu vào gốc ở `documents/sources/`. Khi người dùng xác nhận bản Word đạt, chép sang thư mục mới `versions/documents/<ten>/v<version>/` gồm `<ten>_v<version>.docx` và PDF cùng tên. Bắt đầu từ `1.0.0`, căn cứ bản giao gần nhất: đổi nhỏ (định dạng, sửa lỗi) tăng PATCH `1.0.0 → 1.0.1`; sửa/bổ sung một phần nội dung tăng MINOR và reset PATCH `1.0.1 → 1.1.0`; đổi mục tiêu hoặc cấu trúc toàn bộ tăng MAJOR và reset hai số sau `1.1.0 → 2.0.0`. Bản xem thử/gửi duyệt không tính là phiên bản. Không sửa trong `versions/`, không ghi đè bản đã giao, không đánh số lại bản lịch sử khi chưa được yêu cầu.

## Phiên bản firmware

Mỗi phiên bản firmware có một thư mục code riêng trong project: `<project>/firmware/v<version>/` (`src/`, `common/`, README). Chỉ sửa thư mục mới nhất; thư mục cũ đóng băng, không sửa. Bắt đầu phiên bản mới bằng cách chép thư mục hiện tại sang `v<version mới>/` rồi trỏ build sang đó; `firmware/README.md` có bảng các phiên bản (thư mục, nội dung, env build).

Số phiên bản đặt ở một chỗ (PlatformIO: `custom_fw_version` trong `platformio.ini`, script `pre:` chuyển thành `FW_VERSION`), in ra Serial lúc boot. Mỗi lần build chép `.bin`/`.elf` sang `releases/v<version>/<project>-<env>-v<version>.bin` (không đưa vào Git). Firmware chưa phát hành bắt đầu từ `0.1.0`; sửa lỗi tăng PATCH, thêm tính năng tăng MINOR, đổi không tương thích (định dạng gói tin, sơ đồ chân) tăng MAJOR. Khi merge một phiên bản vào nhánh chính: gắn tag `v<version>` và đưa `.bin` lên GitHub Release cùng tag; bản giao cho người dùng chép vào `versions/firmware/<project>/v<version>/`.

Giữ env build cho mỗi phiên bản cũ còn biên dịch được (tên env PlatformIO không được có dấu chấm: `esp32dev-v0_2_0`). Phiên bản cũ không biên dịch được thì chỉ lưu trữ và ghi rõ trong bảng.

## Cấu trúc

```text
AGENTS.md                         Quy tắc chung
.agents/skills/                   Skill local bản gốc
.claude/skills/                   File dẫn hướng skill cho Claude
firmware/v0.2.0/at89s52/                 Firmware AT89S52 (main.c)
firmware/v0.2.0/esp32/                   Firmware ESP32-C3 (PlatformIO)
dashboard/                        Dashboard ThingsBoard và bản local
hardware/                         BOM, bảng giá, generate.py
hardware/pcb/                     Dự án KiCad 10 (env-monitor): sơ đồ nguyên lý nối bằng global label, PDF xuất kèm
tests/                            Kiểm thử
docs/                             Tài liệu kỹ thuật đang duy trì
.planning/                        Trạng thái AXON
documents/sources/                Ảnh và tư liệu gốc kèm ghi chú
documents/verification/           Báo cáo kiểm thử
sandbox/                          Thử nghiệm, bản nháp và bản làm dở
sandbox/simulation/               Mô phỏng và thử nghiệm độc lập
versions/                         Bản đã giao/phát hành, luôn theo vX.Y.Z; không sửa, không ghi đè
documents/<ten>/                  Tài liệu Word đang soạn (kế hoạch, figures, drafts)
versions/documents/<ten>/         Mỗi bản giao gồm DOCX và PDF
versions/firmware/<project>/      Mỗi bản giao gồm .bin theo phiên bản
considerations/                   Ý tưởng và vấn đề chưa chốt
```

## Công cụ và MCP

Kiểm tra công cụ hiện có trước khi ghi lệnh hoặc cấu hình. Chưa khai báo công cụ hay MCP cụ thể trong mẫu này; không tự cài đặt hoặc ghi cấu hình giả.

## Skill local

| Skill | Dùng khi |
| --- | --- |
| `workspace-guide` | Tìm đúng thư mục, đọc quy tắc và sắp xếp tư liệu trong workspace này. |

Bản gốc ở `.agents/skills/<name>/SKILL.md`; `.claude/skills/` chỉ dẫn hướng. Client không tự nạp skill thì đọc bản gốc khi công việc phù hợp.

Skill cá nhân dùng chung nằm trong collection ngoài project (máy hiện tại: `D:\Personal-Skills`), riêng với AXON. `.agents/skills/` chỉ giữ skill local của workspace. Kiểm tra symlink/junction trước khi di chuyển skill đã cài; không kéo theo repo, môi trường chạy hoặc cấu hình riêng của công cụ khác. Không push Git khi chưa được yêu cầu.

## Cập nhật skill

Khi có bài học liên quan trực tiếp tới skill hiện có, cập nhật skill đó trong phạm vi được giao. Nếu cần skill mới ngoài yêu cầu hiện tại, đề xuất mục đích trước; chỉ tạo khi người dùng yêu cầu hoặc xác nhận. Quy tắc chung giữ tại AGENTS.md, không sao chép thành nhiều bộ quy tắc.
