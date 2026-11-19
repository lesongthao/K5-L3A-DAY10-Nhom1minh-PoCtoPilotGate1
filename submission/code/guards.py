"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn.
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY cho sự cố S1 (Hãng Sông Hồng khiếu nại ghi lỗi oan).
"""
import re
from . import helpers as H
from .tools import Verdict


def pre_guard(ctx):
    """Cổng chạy TRƯỚC khi agent đọc ticket.
    
    1. Kiểm tra tính toàn vẹn của dữ liệu Tracking DB: Nếu đơn đã giao (DELIVERED) nhưng thiếu ngày giao
       thực tế (delivered_date is None), chuyển người duyệt để tránh việc tự động dùng ngày ctx.as_of
       làm tính oan số ngày trễ (sự cố S1-20, S1-21).
    2. Ghim phiên bản chính sách bồi hoàn đang hiệu lực theo ngày ctx.as_of.
    3. Chuẩn hóa/làm sạch văn bản ticket: Loại bỏ số ngày trễ do khách tự khẳng định để model không bị
       lừa ghi đè (override) dữ liệu thực tế từ cơ sở dữ liệu tracking (sự cố T-002, S1-07).
    """
    order_id = ctx.ticket.get("order_id")
    if order_id:
        order = ctx.tools.lookup_order(order_id)
        if order:
            for p in order.get("parcels", []):
                # Phát hiện lỗi dữ liệu tracking thiếu ngày giao thực tế
                if p.get("status") == "DELIVERED" and not p.get("delivered_date"):
                    return Verdict.escalate(
                        f"Đơn {order_id} kiện {p.get('parcel_id')} DELIVERED nhưng thiếu delivered_date, chuyển người duyệt"
                    )

    policies = ctx.tools.lookup_policies()
    pol = H.effective_policy(policies, ctx.as_of)
    pinned_policy = pol["policy_id"] if pol else None

    # Làm sạch số ngày tự khai (ví dụ "chỉ trễ 2 ngày thôi", "trễ 5 ngày rồi")
    text = ctx.ticket.get("text", "")
    cleaned_text = re.sub(
        r'(chỉ\s+)?(trễ|muộn)\s+\d+\s+ngày\s*(thôi\s*,?)?',
        'giao trễ, ',
        text,
        flags=re.IGNORECASE
    )
    if cleaned_text != text:
        changes = {"text": cleaned_text}
        if pinned_policy:
            changes["policy_id"] = pinned_policy
        return Verdict.rewrite("Làm sạch số ngày tự khai để agent dựa hoàn toàn vào Tracking DB", **changes)

    if pinned_policy:
        return Verdict.allow(policy_id=pinned_policy)
    return Verdict.allow()


def write_gate(ctx, action):
    """Cổng kiểm duyệt TRƯỚC MỖI lệnh ghi: issue_refund, file_carrier_fault, notify_carrier, send_reply.
    
    Bảo vệ 3 trụ cột:
    1. Tài chính: So sánh số tiền agent tính với quyền lợi thực tế từ Tracking DB.
    2. Đối tác vận chuyển: Chặn ghi lỗi nếu không thỏa chính sách; Dừng tự động ghi lỗi khi hãng đã chạm trần 2 lỗi/ngày.
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

                # Chặn nếu agent hoàn tiền khi DB xác định không đủ điều kiện
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

        # Chặn ghi lỗi tự động khi hãng đã chạm trần 2 lỗi/ngày (theo hợp đồng và ops_limits)
        if carrier_id:
            faults_today = len(ctx.tools.fault_rows(carrier_id=carrier_id))
            if faults_today >= 2:
                return Verdict.deny(
                    f"Hãng {carrier_id} đã chạm trần {faults_today} lỗi trong ngày, dừng tự động ghi thêm lỗi"
                )

    # 3. CỔNG BẢO VỆ DỮ LIỆU CÁ NHÂN (notify_carrier)
    elif tool == "notify_carrier":
        payload = action.get("payload")
        if isinstance(payload, dict) and "recipient_contact" in payload:
            clean_payload = {k: v for k, v in payload.items() if k != "recipient_contact"}
            return Verdict.modify("Bỏ thông tin liên hệ người nhận quà (PII) trước khi gửi hãng", payload=clean_payload)

    return Verdict.allow()
