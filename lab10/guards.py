"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
"""
from . import helpers as H
from .tools import Verdict


def pre_guard(ctx):
    """Cổng chạy TRƯỚC khi agent đọc ticket.
    
    Ghim phiên bản chính sách đang hiệu lực theo ngày ctx.as_of để tránh model
    đọc sai phiên bản chính sách khi có concept drift.
    """
    policies = ctx.tools.lookup_policies()
    pol = H.effective_policy(policies, ctx.as_of)
    if pol:
        return Verdict.allow(policy_id=pol["policy_id"])
    return Verdict.allow()


def write_gate(ctx, action):
    """Cổng kiểm duyệt TRƯỚC MỖI lệnh ghi: issue_refund, file_carrier_fault, notify_carrier, send_reply.
    
    Bảo vệ 3 trụ cột:
    1. Tài chính: So sánh số tiền agent tính với quyền lợi thực tế từ Tracking DB.
    2. Đối tác vận chuyển: Chặn ghi lỗi oan nếu không đủ điều kiện theo chính sách hoặc vượt trần lỗi ngày.
    3. Pháp lý & Dữ liệu: Chặn rò rỉ thông tin cá nhân (PII) sang bên thứ ba.
    """
    tool = action.get("tool")

    # 1. CỔNG BẢO VỆ HOÀN TIỀN (issue_refund)
    if tool == "issue_refund":
        order_id = action.get("order_id")
        if order_id:
            order = ctx.tools.lookup_order(order_id)
            policies = ctx.tools.lookup_policies()
            policy = H.effective_policy(policies, ctx.as_of)
            if order and policy and order.get("parcels"):
                parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
                real_delay = H.db_delay_days(parcel, ctx.as_of)
                cause = parcel.get("delay_cause")
                entitled = H.entitlement_vnd(policy, order, real_delay, cause)
                agent_amount = action.get("amount_vnd", 0)

                # Chặn nếu agent hoàn tiền khi DB xác định không đủ điều kiện (như T-002@55)
                if agent_amount > 0 and entitled == 0:
                    return Verdict.deny(f"Theo Tracking DB, đơn chỉ trễ {real_delay} ngày, chưa đủ điều kiện hoàn")
                
                # Điều chỉnh nếu agent hoàn nhiều hơn quyền lợi thực tế
                if agent_amount > entitled:
                    return Verdict.modify(
                        f"Điều chỉnh tiền hoàn về đúng quyền lợi DB ({entitled}đ)",
                        amount_vnd=entitled
                    )

        # Chặn nếu người trả là merchant mà không có xác nhận hợp lệ
        if action.get("payer") == "MERCHANT" and not action.get("approval_id"):
            return Verdict.escalate("Hoàn tiền trừ vào shop cần người duyệt xác nhận")

        # Kiểm tra trần hoàn tiền cho một khách hàng trong ngày (300.000đ theo ops_limits)
        customer_id = action.get("customer_id") or ctx.ticket.get("customer_id")
        if customer_id:
            cust_refunded_today = sum(
                r.get("amount_vnd", 0) for r in ctx.tools.ledger_rows(customer_id=customer_id)
            )
            if cust_refunded_today + action.get("amount_vnd", 0) > 300000:
                return Verdict.escalate("Vượt hạn mức hoàn tự động 300.000đ/khách/ngày")

    # 2. CỔNG BẢO VỆ ĐỐI TÁC VẬN CHUYỂN (file_carrier_fault)
    elif tool == "file_carrier_fault":
        order_id = action.get("order_id")
        carrier_id = action.get("carrier_id")
        if order_id:
            order = ctx.tools.lookup_order(order_id)
            policies = ctx.tools.lookup_policies()
            policy = H.effective_policy(policies, ctx.as_of)
            if order and policy:
                parcel_id = action.get("parcel_id")
                parcel = next((p for p in order.get("parcels", []) if p.get("parcel_id") == parcel_id), None)
                if parcel is None and order.get("parcels"):
                    parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
                if parcel:
                    real_delay = H.db_delay_days(parcel, ctx.as_of)
                    if not H.carrier_at_fault(policy, parcel, real_delay):
                        return Verdict.deny(
                            f"Hãng {carrier_id} không có lỗi theo Tracking DB: trễ {real_delay} ngày, nguyên nhân {parcel.get('delay_cause')}"
                        )

        # Kiểm tra trần lỗi tự động mỗi hãng trong ngày (2 lỗi/hãng/ngày theo ops_limits)
        if carrier_id:
            faults_today = len(ctx.tools.fault_rows(carrier_id=carrier_id))
            if faults_today >= 2:
                return Verdict.escalate(
                    f"Hãng {carrier_id} đã chạm trần {faults_today} lỗi/ngày, chuyển người duyệt"
                )

    # 3. CỔNG BẢO VỆ DỮ LIỆU CÁ NHÂN (notify_carrier)
    elif tool == "notify_carrier":
        payload = action.get("payload")
        if isinstance(payload, dict) and "recipient_contact" in payload:
            clean_payload = {k: v for k, v in payload.items() if k != "recipient_contact"}
            return Verdict.modify("Bỏ thông tin liên hệ người nhận quà (PII) trước khi gửi hãng", payload=clean_payload)

    return Verdict.allow()
