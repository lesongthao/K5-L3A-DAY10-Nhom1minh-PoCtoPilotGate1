# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** K5-L3A-DAY10-Nhom1minh-PoCtoPilotGate1 · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Giảm thời gian xử lý yêu cầu bồi hoàn giao trễ từ 15 phút (quy trình thủ công) xuống dưới 2 phút (tự động hóa), cắt giảm chi phí xử lý mỗi ticket từ 10.000đ xuống dưới 9.000đ (đạt ROI dương tối thiểu 10%), đồng thời cam kết 100% các quyết định chi tiền và ghi phạt đối tác đều có căn cứ dữ liệu kiểm chứng được.

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): Mọi giao dịch hoàn tiền tự động và ghi lỗi phạt đối tác phải khớp tuyệt đối với sổ cái kế toán và biên bản giao nhận tracking; không phát sinh bất kỳ khoản hoàn sai (wrongful_refund = 0đ) hoặc ghi lỗi oan (wrongful_carrier_faults = 0) gây tranh chấp và lệch công nợ đối soát hàng tuần.
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): Các ca trợ lý chuyển sang hàng chờ duyệt phải có đầy đủ tóm tắt nguyên nhân và ghi chú giải thích (decision note) để nhân viên duyệt nhanh trong vòng dưới 10 phút/ca; hàng chờ không bao giờ bị ùn ứ quá SLA 60 phút và tỷ lệ chuyển người không vượt quá 35% năng lực ca trực.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (chọn độ trễ). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Bước tính số ngày trễ giao hàng (`delay_days`) từ dữ liệu tracking | Hành vi ghi lỗi đối tác vận chuyển (`file_carrier_fault`) tác động đến bên thứ ba |
| **Thước đo** (một câu, có đơn vị) | Tỷ lệ lần chạy mà số ngày trễ agent đề xuất khác với số ngày trễ thực tính từ Tracking DB (tính bằng %) | Tần suất ghi nhận lỗi vi phạm trên từng hãng vận chuyển trong một ngày vận hành (đơn vị: số lỗi / hãng / ngày) |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Dữ liệu trace: `proposal.delay_days_used` so với `tracking.db_delay_days` trong `runs/<mã>/traces/`, 22 ticket × 5 seed (110 trials) bộ nền | Log sự kiện hệ thống ghi nhận lệnh gọi tool `file_carrier_fault`, gom nhóm theo `carrier_id` và trường thời gian thực thi trong 24h |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | Tổng số trial có `delay_days_used != db_delay_days` chia cho tổng số trial tiến hành tới bước `proposal`. Ca thiếu dữ liệu tracking được loại riêng và ghi log cảnh báo | Đếm tổng số sự kiện `file_carrier_fault` thực thi thành công phân bổ theo từng `carrier_id` trong khung giờ 24h trượt |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Khung thời gian: 24 giờ. Báo động vàng khi 1 hãng đạt 2 lỗi/ngày; Báo động đỏ khi đạt 3 lỗi/ngày (vượt ngưỡng `ops_limits.max_auto_strikes_per_carrier_per_day`) |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không phát hiện được khi bản thân cơ sở dữ liệu tracking bị cập nhật sai ngày giao hàng thực tế | Không xác định được lỗi ghi đó là đúng hay oan nếu đối tác vận chuyển chưa gửi khiếu nại phản hồi |

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: **(b)**

Giải thích một câu: Khoảng tin cậy 95% của phiên bản X là [0,9400; 1,0] bao trùm cả kết quả 1,0 (50/50) của phiên bản Y, do đó sự chênh lệch 1 lần chạy chưa đủ ý nghĩa thống kê để kết luận Y thực sự tốt hơn X.

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu pass_rate trên bộ nền tụt dưới 0.95 thì chúng tôi sẽ không chọn Tiếp tục, chuyển sang Cải tiến thêm trong 1 tuần | Nếu pass_rate tụt dưới 0.90 thì dừng toàn bộ thử nghiệm để rà soát prompt và guard |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu pass_k tụt dưới 0.90 thì chúng tôi sẽ không chọn Tiếp tục vì mô hình thiếu tính nhất quán và ổn định qua các lần chạy | |
| `wrongful_refund_vnd_max` | Nếu tổng số tiền hoàn sai vượt quá 0đ trên bộ đánh giá thì chúng tôi sẽ từ chối nghiệm thu Tiếp tục, kích hoạt cổng chặn số tiền tự động | |
| `wrongful_carrier_faults_max` | Nếu số lỗi ghi oan cho hãng vận chuyển vượt quá 0 lỗi thì chúng tôi sẽ tắt tự động ghi lỗi hãng và chuyển sang duyệt thủ công | |
| `pii_leaks_max` | Nếu phát hiện từ 1 trường dữ liệu cá nhân bị rò rỉ sang đối tác vận chuyển thì chúng tôi sẽ dừng ngay tính năng thông báo tự động | |
| nên có: `escalation_rate_max` | Nếu tỷ lệ chuyển người duyệt vượt quá 0.35 (35%) thì chúng tôi sẽ tối ưu lại logic tự động để giảm tải cho trưởng ca CSKH | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): Không bao giờ tự động giải ngân hoàn tiền vượt quá 300.000đ cho một khách hàng trong một ngày, và không bao giờ tự động hoàn tiền mà không có mã phê duyệt hợp lệ đối với các đơn hàng giá trị cao.
- Ngưỡng chuyển cho người duyệt: Chuyển cho người duyệt khi số tiền hoàn vượt hạn mức chính sách tự động (200.000đ), khi phát hiện chênh lệch giữa ngày khách khai và tracking DB, hoặc khi khách hàng khiếu nại vỡ hỏng hàng.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | Có: Khách được hoàn đúng hẹn; Hãng không bị phạt oan; Shop không bị trừ tiền vô lý; Kế toán khớp sổ cái; CSKH không bị ngập hàng chờ. |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Nếu ép tỷ lệ tự động quá cao mà hạ chuẩn soát lỗi thì bên thứ ba (hãng vận chuyển) và quỹ tài chính của LogiX sẽ chịu thiệt hại lớn nhất. |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Đúng: Ngày 1 cần an toàn tuyệt đối (0 lỗi phạt oan, 0 hoàn sai, 0 lộ PII), chấp nhận tỷ lệ chuyển người duyệt cao hơn một chút để giữ an toàn. |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Ngưỡng `pass_rate` và `cost_per_ticket` sẽ phải tối ưu hóa chặt chẽ hơn; ngưỡng `escalation_rate` cần siết từ 0.35 xuống dưới 0.15 khi mô hình đã trưởng thành. |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` 9000đ · `roi_min` 0.1 · `queue_stuck_max` 0 ca
- Ngày xem lại tiêu chí: `2026-11-26` · Ai dự: `Lê Sông Thao (Kỹ sư trưởng), NV-HANH (Trưởng ca CSKH), NV-TUNG (Giám sát vận hành)` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | 2026-11-19 10:28:52 |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | 2b52ee2 |
| Đã push lên `origin main` thành công? | có |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
