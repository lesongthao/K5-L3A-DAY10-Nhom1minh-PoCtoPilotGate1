# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): Nhom1minh
- Lớp: `L3A`
- Repo của bàn: `K5-L3A-DAY10-Nhom1minh-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S1

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Lê Sông Thao | 2A202603534 | Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý | ✓ |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## LeSongThao-2A202603534

### Phần việc phụ trách

Làm 1 mình, đảm nhận cả 3 vai: Kỹ sư cổng (câu 2.1–2.2, 2.6–2.8, 3.1, 3.5–3.6), Sản phẩm và kinh doanh (câu 1.1, 1.3, 1.6, 2.3, 2.9, 3.2), Vận hành và pháp lý (câu 1.2, 1.4, 2.4, 2.10, 3.3, 3.7). Toàn bộ Phiếu A, B, C. File: `lab10/guards.py`, `lab10/monitors.py`, `config/operating_gates.json`, `config/acceptance_criteria.json`, `submission/submission.json`.

### Đóng góp cụ thể

Viết 3 cổng phòng ngừa trong guards.py (cổng hoàn tiền, cổng lỗi hãng, cổng PII). Điền toàn bộ config operating_gates.json. Thêm chỉ số theo dõi mới trong monitors.py. Điền 3 phiếu A, B, C. Có sử dụng AI (Antigravity) hỗ trợ viết code, soát cấu trúc và giải thích logic cổng.

### Bằng chứng

Mã commit, mã lần chạy sẽ ghi trong phiếu B mục B0 và phiếu C mục C0.

### Exit ticket

- Học được: Viết tiêu chí chấp nhận TRƯỚC khi nhìn kết quả giúp tránh thiên kiến xác nhận; cổng phòng ngừa (guardrails) nằm NGOÀI model mới là lớp bảo vệ đáng tin cậy nhất.
- Còn chưa chắc: Cách cân bằng giữa số người trực (chi phí) và thời gian chờ hàng chờ (SLA) khi lượng ticket tăng đột biến.
