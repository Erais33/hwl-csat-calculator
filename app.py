import streamlit as st
import pandas as pd
from datetime import datetime

# ---- BRAND STYLE ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }

    .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
    }

    input, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }

    .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        padding: 1em !important;
    }

    div[data-testid="stAlert-success"] {
        background-color: #E6F4EA !important;
        color: #000000 !important;
    }
    div[data-testid="stAlert-info"] {
        background-color: #E7F2FA !important;
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- LOGO ----
st.image("https://seeklogo.com/images/H/hostelworld-logo-57FDE8F7B1-seeklogo.com.png", width=200)

st.title("St Christopher's Inns • Rolling Average Forecast")

# ---- EXPLANATION ----
st.header("📖 What is the Target Rolling Average?")
st.markdown(
    """
    Your rolling average is your average guest score over the last 6 months.
    The **Target Rolling Average** is the score you want to reach for next month.
    
    This tool shows:
    - 📉 If you add **no new reviews**, what your average may drop to.
    - ⭐️ If you want to hit your target, how many new reviews you’d need, and what average they must reach.
    """
)

# ---- UPLOAD ----
st.header("📤 Upload Reviews CSV")
uploaded_file = st.file_uploader("Upload your Hostelworld CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            usecols=[
                "Date", "Nationality", "Age",
                "Value For Money", "Security", "Location", "Staff",
                "Atmosphere", "Cleanliness", "Facilities", "Ratings"
            ],
            parse_dates=["Date"],
            dayfirst=True,
            engine='python',  # more robust
            on_bad_lines='warn'
        )

        st.success(f"✅ File uploaded! Total rows read: {len(df)}")

        # Coerce scores to numbers
        score_cols = [
            "Value For Money", "Security", "Location",
            "Staff", "Atmosphere", "Cleanliness", "Facilities", "Ratings"
        ]
        for col in score_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=["Date", "Ratings"])

        st.write(f"Valid reviews after cleaning: {len(df)}")

        # ---- DATE PICKER ----
        st.header("📅 Forecast Date")
        cutoff_date = st.date_input("Forecast for date:", datetime.today().date())
        six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)

        current_reviews = df[(df["Date"] > six_months_ago) & (df["Date"] <= pd.to_datetime(cutoff_date))]
        dropping_reviews = df[df["Date"] <= six_months_ago]

        current_avg = current_reviews["Ratings"].mean()
        current_count = len(current_reviews)

        dropped_avg = dropping_reviews["Ratings"].mean()
        dropped_count = len(dropping_reviews)

        st.header("🧾 Summary")
        st.success(f"✅ Staying reviews: {current_count} | Avg: {current_avg:.2f} / 10.00")
        st.info(f"🔻 Dropping reviews: {dropped_count} | Avg: {dropped_avg:.2f} / 10.00")

        # ---- SUB-CATEGORIES ----
        st.header("📊 Sub-category Averages (Last 6 Months)")
        for col in score_cols[:-1]:  # exclude Ratings
            avg = current_reviews[col].mean()
            st.write(f"**{col}**: {avg:.2f} / 10.00")

        # ---- TARGET ----
        st.header("🎯 Set Your Target")
        target_avg = st.number_input(
            "Target rolling average:",
            value=9.00, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )
        expected_new_avg = st.number_input(
            "Expected average for new reviews:",
            value=9.20, min_value=0.1, max_value=10.0, step=0.1, format="%.2f"
        )

        # ---- CALCULATION ----
        total_current = current_avg * current_count
        total_drop = dropped_avg * dropped_count
        rolling_total_after_drop = total_current - total_drop
        base_reviews_remaining = current_count - dropped_count
        if base_reviews_remaining < 0:
            base_reviews_remaining = 0

        needed_points = target_avg * (base_reviews_remaining + 1) - rolling_total_after_drop

        if expected_new_avg > target_avg:
            needed_reviews = needed_points / (expected_new_avg - target_avg)
            needed_reviews = max(0, needed_reviews)
        else:
            needed_reviews = 0

        new_avg_if_none = (
            rolling_total_after_drop / base_reviews_remaining if base_reviews_remaining > 0 else 0.0
        )

        st.header("📈 Forecast")
        st.success(
            f"📉 If you add no new reviews, your rolling average would drop to: **{new_avg_if_none:.2f} / 10.00**"
        )
        if needed_reviews > 0:
            st.info(
                f"⭐️ To reach **{target_avg:.2f}**, you’d need about **{needed_reviews:.0f}** "
                f"new reviews averaging **{expected_new_avg:.2f} / 10.00**."
            )
        else:
            st.warning("⚠️ Your expected average must be higher than your target to calculate realistically.")

    except Exception as e:
        st.error(f"❌ Error reading your CSV: {e}")
else:
    st.info("📂 Upload your CSV to begin your forecast.")

st.markdown("<sub>Made by Erwan Decotte • St Christopher's Inns</sub>", unsafe_allow_html=True)
