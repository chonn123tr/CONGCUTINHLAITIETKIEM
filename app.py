
import streamlit as st
import pandas as pd
st.image("logo.jpg")

# =========================
# CẤU HÌNH TRANG WEB
# =========================
st.set_page_config(
    page_title="Tính lãi gửi tiết kiệm",
    page_icon="💰",
    layout="centered"
)

st.title("💰 MÁY TÍNH LÃI TIẾT KIỆM _ TRẦN THANH AN")
st.write(
    "Tính toán số tiền lãi và tổng số tiền nhận được "
    "dựa trên số tiền gửi, kỳ hạn và lãi suất."
)

st.divider()


# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_money(amount):
    return f"{amount:,.0f} VNĐ".replace(",", ".")


# =========================
# NHẬP THÔNG TIN
# =========================
st.subheader("1. Thông tin tiền gửi")

with st.form("savings_form"):
    principal = st.number_input(
        "Số tiền gửi ban đầu (VNĐ)",
        min_value=100_000,
        max_value=1_000_000_000_000,
        value=10_000_000,
        step=1_000_000,
        help="Số tiền gốc em dự định gửi tiết kiệm."
    )

    col1, col2 = st.columns(2)

    with col1:
        term_months = st.number_input(
            "Kỳ hạn gửi (tháng)",
            min_value=1,
            max_value=600,
            value=12,
            step=1
        )

    with col2:
        annual_rate = st.number_input(
            "Lãi suất (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.1,
            format="%.2f"
        )

    interest_type = st.selectbox(
        "Phương pháp tính lãi",
        ["Lãi đơn", "Lãi kép"],
        help=(
            "Lãi đơn tính lãi trên số tiền gốc ban đầu. "
            "Lãi kép nhập lãi vào vốn để tiếp tục sinh lãi."
        )
    )

    payout_type = st.selectbox(
        "Hình thức nhận lãi / chu kỳ nhập lãi",
        ["Cuối kỳ", "Hàng tháng", "Hàng quý"],
        help=(
            "Với lãi đơn, tiền lãi được tính theo gốc ban đầu. "
            "Với lãi kép, lãi được nhập vào vốn theo chu kỳ "
            "đã chọn; nếu chọn cuối kỳ, lãi kép được nhập vốn "
            "hàng tháng và nhận toàn bộ khi đáo hạn."
        )
    )

    submitted = st.form_submit_button(
        "TÍNH TIỀN LÃI",
        use_container_width=True
    )


# =========================
# TÍNH TOÁN
# =========================
if submitted:
    rate = annual_rate / 100
    months = int(term_months)

    # Xác định số tháng trong mỗi chu kỳ
    if payout_type == "Hàng tháng":
        period_months = 1
    elif payout_type == "Hàng quý":
        period_months = 3
    else:
        period_months = 1

    # Tạo danh sách các kỳ tính lãi.
    # Kỳ cuối có thể ngắn hơn 1 quý nếu kỳ hạn
    # không chia hết cho 3 tháng.
    if interest_type == "Lãi đơn":
        periods = list(range(0, months, period_months))
        periods = [
            min(period_months, months - start)
            for start in periods
        ]
    elif payout_type == "Cuối kỳ":
        periods = [1] * months
    else:
        periods = list(range(0, months, period_months))
        periods = [
            min(period_months, months - start)
            for start in periods
        ]

    balance = float(principal)
    total_interest = 0.0
    detail = []
    elapsed_months = 0
    first_period_interest = 0.0

    for index, duration in enumerate(periods, start=1):
        start_balance = balance

        if interest_type == "Lãi đơn":
            # Lãi đơn: luôn tính lãi trên vốn gốc ban đầu
            interest = principal * rate * duration / 12
            balance = principal
        else:
            # Lãi kép: nhập lãi vào vốn sau mỗi kỳ.
            # Lãi suất được quy đổi theo số tháng của kỳ.
            interest = start_balance * (
                (1 + rate / 12) ** duration - 1
            )
            balance = start_balance + interest

        if index == 1:
            first_period_interest = interest

        total_interest += interest
        elapsed_months += duration

        detail.append({
            "Kỳ": index,
            "Thời gian": f"Tháng {elapsed_months}",
            "Số tháng": duration,
            "Tiền đầu kỳ (VNĐ)": round(start_balance),
            "Tiền lãi kỳ này (VNĐ)": round(interest),
            "Tổng tiền cuối kỳ (VNĐ)": round(balance)
        })

    total_amount = principal + total_interest

    # Với lãi kép, balance là tổng tiền đã cộng dồn.
    if interest_type == "Lãi kép":
        total_amount = balance
        total_interest = total_amount - principal

    # Tiền lãi định kỳ:
    # - Lãi đơn: số tiền lãi mỗi tháng/quý.
    # - Lãi kép: tiền lãi của kỳ đầu tiên.
    if interest_type == "Lãi đơn":
        if payout_type == "Hàng tháng":
            periodic_interest = principal * rate / 12
            periodic_label = "Tiền lãi mỗi tháng"
        elif payout_type == "Hàng quý":
            periodic_interest = principal * rate / 4
            periodic_label = "Tiền lãi mỗi quý"
        else:
            periodic_interest = total_interest
            periodic_label = "Tiền lãi khi đáo hạn"
    else:
        periodic_interest = first_period_interest
        if payout_type == "Hàng tháng":
            periodic_label = "Tiền lãi kỳ tháng đầu"
        elif payout_type == "Hàng quý":
            periodic_label = "Tiền lãi kỳ quý đầu"
        else:
            periodic_label = "Tiền lãi tháng đầu (tái nhập vốn)"

    # =========================
    # HIỂN THỊ KẾT QUẢ
    # =========================
    st.divider()
    st.subheader("2. Kết quả tính toán")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label=periodic_label,
            value=format_money(periodic_interest)
        )

    with col2:
        st.metric(
            label="Tổng tiền lãi",
            value=format_money(total_interest)
        )

    with col3:
        st.metric(
            label="Tổng gốc + lãi",
            value=format_money(total_amount)
        )

    st.caption(
        f"Số tiền gốc: {format_money(principal)} | "
        f"Kỳ hạn: {months} tháng | "
        f"Lãi suất: {annual_rate:.2f}%/năm"
    )

    # =========================
    # BẢNG CHI TIẾT
    # =========================
    st.subheader("3. Chi tiết các kỳ tính lãi")

    df = pd.DataFrame(detail)

    st.dataframe(
        df.style.format({
            "Tiền đầu kỳ (VNĐ)": "{:,.0f}",
            "Tiền lãi kỳ này (VNĐ)": "{:,.0f}",
            "Tổng tiền cuối kỳ (VNĐ)": "{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # GIẢI THÍCH CÁCH TÍNH
    # =========================
    with st.expander("Xem công thức tính lãi"):
        st.markdown(
            """
            **Lãi đơn**

            Tiền lãi = Tiền gốc × Lãi suất năm × Số tháng / 12

            **Lãi kép**

            Với kỳ tính lãi dài `m` tháng:

            Tiền cuối kỳ = Tiền đầu kỳ × (1 + r/12)^m

            Trong đó `r` là lãi suất năm ở dạng số thập phân.

            Lãi suất được giả định không đổi trong suốt kỳ hạn.
            Kết quả chưa tính thuế, phí hoặc các điều kiện riêng
            của ngân hàng.
            """
        )

    st.info(
        "Lưu ý: Đây là công cụ ước tính theo công thức toán học, "
        "không phải báo giá hay cam kết lãi suất của ngân hàng. "
        "Với lãi kép, tiền lãi được tái đầu tư thay vì chi trả "
        "ra ngoài định kỳ."
    )
