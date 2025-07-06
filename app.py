import streamlit as st
import pandas as pd
from datetime import datetime

# ---- PAGE STYLE ----
st.set_page_config(page_title="Rolling Average Forecast", layout="centered")

st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    .block-container {
        background-color: #FFFFFF;
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
        background-color: #F58220 !important;
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- HEADER ----
st.title("📊 Rolling Average Forecast")

# ---- UPLOAD ----
st.header("📤 Upload Reviews CSV")

uploaded_file = st.file_uploader("Upload your Hostelworld CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            usecols=["Date", "Ratings",
                     "Value For Money", "Security", "Location",
                     "Staff", "Atmosphere", "Cleanliness", "Facilities"],
            parse_dates=["Date"],
            dayfirst=True,
            on_bad_lines='skip'
        )

        st.write(f"✅ File uploaded! Total rows: {len(df)}")

        df["Ratings"] = pd.to_numeric(df["Ratings"], errors='coerce')
        valid_reviews = df.dropna(subset=["Ratings", "Date"])

        st.write(f"Valid reviews: {len(valid_reviews)}")
        if len(valid_reviews) != len(df):
            st.warning(f"{len(df) - len(valid_reviews)} rows skipped due to missing or invalid data.")

        # ---- DATE ----
        st.header("📅 Select forecast date")
        st.caption("Pick the future date. Reviews older than 6 months will drop off on that date.")

        default_date = datetime.today().date()
        cutoff_date = st.date_input("Select forecast date:", default_date)

        six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)

        current_reviews_df = valid_reviews[
            (valid_reviews["Date"] > six_months_ago) & (valid_reviews["Date"] <= pd.to_datetime(cutoff_date))
        ]
        dropping_reviews_df = valid_reviews[valid_reviews["Date"] <= six_months_ago]

        current_avg = current_reviews_df["Ratings"].mean() if not current_reviews_df.empty else 0.0
        current_reviews_count = len(current_reviews_df)

        dropped_reviews_count = len(dropping_reviews_df)
        dropped_reviews_avg = dropping_reviews_df["Ratings"].mean() if not dropping_reviews_df.empty else 0.0

        st.header("📊 Current Metrics")
        st.write(f"• Staying reviews: **{current_reviews_count}** | Avg: **{current_avg:.2f} / 10.00**")
        st.write(f"• Dropping reviews: **{dropped_reviews_count}** | Avg: **{dropped_reviews_avg:.2f} / 10.00**")

        # ---- SUBCATEGORY AVERAGES ----
        st.subheader("🗂️ Subcategory Averages (last 6 months)")
        for col in ["Value For Money", "Security", "Location", "Staff",
                    "Atmosphere", "Cleanliness", "Facilities"]:
            avg = current_reviews_df[col].mean() if not current_reviews_df.empty else 0.0
            st.write(f"- **{col}**: {avg:.2f} / 10.00")

        # ---- TARGET INPUT ----
        st.header("🎯 Forecast Inputs")

        target_avg = st.number_input(
            "🎯 Target rolling average:",
            help="This is the score you want your rolling 6-month average to reach.",
            value=9.0, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )

        expected_new_avg = st.number_input(
            "✍️ Expected average for new reviews:",
            help="Estimate the realistic average score you expect from new reviews.",
            value=9.2, min_value=0.1, max_value=10.0, step=0.1, format="%.2f"
        )

        # ---- CALCULATE ----
        current_total = current_avg * current_reviews_count
        drop_total = dropped_reviews_avg * dropped_reviews_count
        rolling_total_after_drop = current_total - drop_total

        base_reviews_remaining = current_reviews_count - dropped_reviews_count
        if base_reviews_remaining < 0:
            base_reviews_remaining = 0

        needed_points_from_new = target_avg * (base_reviews_remaining + 1) - rolling_total_after_drop

        if expected_new_avg > target_avg:
            new_reviews_needed = needed_points_from_new / (expected_new_avg - target_avg)
            new_reviews_needed = max(0, new_reviews_needed)
        else:
            new_reviews_needed = 0

        new_avg_if_none = (
            rolling_total_after_drop / base_reviews_remaining if base_reviews_remaining > 0 else 0.0
        )

        # ---- FORECAST RESULTS ----
        st.header("📈 Forecast")
        st.write(
            f"📉 If you add no new reviews, your rolling average would drop to: **{new_avg_if_none:.2f} / 10.00**"
        )
        if new_reviews_needed > 0:
            st.write(
                f"⭐️ To reach **{target_avg:.2f}**, you’d need about **{new_reviews_needed:.0f}** new reviews "
                f"averaging **{expected_new_avg:.2f} / 10.00**."
            )
        else:
            st.write("⚠️ Your expected average must be higher than your target to calculate realistically.")

    except Exception as e:
        st.error(f"❌ Error reading your CSV: {e}")
else:
    st.info("📂 Upload your CSV to begin your forecast.")

st.markdown(
    "<br><sub>Made by Erwan Decotte</sub>",
    unsafe_allow_html=True
)
