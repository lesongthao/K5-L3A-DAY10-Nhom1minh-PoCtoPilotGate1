"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def ghsh_strike_rate(trials):
    """Chỉ số theo dõi tỷ lệ ghi lỗi phạt đối tác Giao Hàng Sông Hồng (GHSH) trên mỗi ticket.
    
    Phát hiện sớm sự cố lỗi phạt dồn dập vào một hãng vận chuyển cụ thể.
    """
    ghsh_faults = 0
    for t in trials:
        for f in t.get("faults", []):
            cid = f.get("carrier_id") if isinstance(f, dict) else f[0] if isinstance(f, (list, tuple)) else None
            if cid == "GHSH":
                ghsh_faults += 1
    return round(ghsh_faults / max(1, len(trials)), 4)


def incomplete_tracking_rate(trials):
    """Tỉ lệ ticket bị chuyển người duyệt do dữ liệu tracking bị thiếu ngày giao hàng."""
    count = 0
    for t in trials:
        for ev in t.get("events", []):
            if ev.get("type") in ("pre_guard", "gate") and "delivered_date" in str(ev.get("reason", "")):
                count += 1
                break
    return round(count / max(1, len(trials)), 4)


MONITORS = {
    "escalation_rate": escalation_rate,
    "ghsh_strike_rate": ghsh_strike_rate,
    "incomplete_tracking_rate": incomplete_tracking_rate,
}
STARTER_MONITORS = ("escalation_rate",)
