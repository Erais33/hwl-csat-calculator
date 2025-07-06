import streamlit as st
import pandas as pd
from datetime import datetime

# ---- CLEAN BLACK & WHITE STYLE ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: Arial, sans-serif;
    }
    .block-container {
        padding: 2rem;
        border-radius: 8px;
        max-width: 800px;
        margin: auto;
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
        border-radius: 4px !important;
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
try:
    st.image("logohwl.png", width=200)
except:
    st.image("https://seeklogo.com/images/H/hostelworld-logo-57FDE8F7B1-seeklogo.com.png", width=200)

st.title("6-Month Rolling CSAT Forecast")

# ---- FILE UPLOAD ----
st.header("📤 Upload Reviews CSV")
st.markdown(
    "Upload your Hostelworld CSV with **Date**, **Ratings**, and sub-category columns: "
    "**Value For Money**, **Security**, **Location**, **Staff**, **Atmosphere**, **Cleanliness**, **Facilities**."
)

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            parse_dates=["Date"],
            dayfirst=True,
            on_bad_lines='skip'
        )

        st.success(f"✅ File uploaded! Total rows: {len(df)}")

        df["Ratings"] = pd.to_numeric(df["Ratings"], errors="coerce")
        valid_reviews = df.dropna(subset=["Ratings", "Date"])

        st.write(f"Valid reviews: {len(valid_reviews)}")
        if len(valid_reviews) != len(df):
            st.warning(f"{len(df) - len(valid_reviews)} rows skipped due to invalid or missing values.")

        # ---- FORECAST DATE ----
        st.header("📅 Forecast Date")
        st.markdown("Pick the forecast date to see what reviews will drop off your 6-month rolling window.")

        default_date = datetime.today().date()
        cutoff_date = st.date_input("Forecast date:", default_date)

        six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)

        current_reviews_df = valid_reviews[
            (valid_reviews["Date"] > six_months_ago) & (valid_reviews["Date"] <= pd.to_datetime(cutoff_date))
        ]
        dropping_reviews_df = valid_reviews[valid_reviews["Date"] <= six_months_ago]

        current_avg = current_reviews_df["Ratings"].mean() if not current_reviews_df.empty else 0.0
        current_reviews_count = len(current_reviews_df)

        dropped_reviews_count = len(dropping_reviews_df)
        dropped_reviews_avg = dropping_reviews_df["Ratings"].mean() if not dropping_reviews_df.empty else 0.0

        st.header("🧾 Summary")
        st.success(f"✅ **Staying reviews:** {current_reviews_count} | Avg: {current_avg:.2f} / 10.00")
        st.info(f"🔻 **Dropping reviews:** {dropped_reviews_count} | Avg: {dropped_reviews_avg:.2f} / 10.00")

        # ---- SUBCATEGORY AVERAGES ----
        st.header("📊 Subcategory Averages (Last 6 Months)")

        categories = [
            "Value For Money", "Security", "Location",
            "Staff", "Atmosphere", "Cleanliness", "Facilities"
        ]

        for cat in categories:
            if cat in current_reviews_df.columns:
                avg = current_reviews_df[cat].mean()
                st.write(f"**{cat}:** {avg:.2f} / 10.00")
            else:
                st.warning(f"⚠️ Column '{cat}' not found in CSV.")

        # ---- TARGET ----
        st.header("🎯 Set Your Rolling Average Goal")
        st.markdown(
            "Your **Target Rolling Average** is the score you'd like your rolling 6-month average to be **after this forecast date**.\n\n"
            "Example: If you want to reach 8.5, this shows how many new reviews you’d need, and the expected average "
            "you must achieve."
        )

        target_avg = st.number_input(
            "Target rolling average:",
            value=9.50, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )

        expected_new_avg = st.number_input(
            "Expected average for new reviews:",
            value=9.20, min_value=0.1, max_value=10.0, step=0.1, format="%.2f"
        )

        # ---- CALCULATION ----
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

        total_score_needed = new_reviews_needed * expected_new_avg

        new_avg_if_none = (
            rolling_total_after_drop / base_reviews_remaining if base_reviews_remaining > 0 else 0.0
        )

        # ---- RESULTS ----
        st.header("📈 Forecast Results")
        st.success(
            f"📉 If you add no new reviews, your rolling average will drop to: **{new_avg_if_none:.2f} / 10.00**"
        )

        if new_reviews_needed > 0:
            st.info(
                f"⭐️ To reach **{target_avg:.2f}**, you’d need about **{new_reviews_needed:.0f}** new reviews "
                f"averaging **{expected_new_avg:.2f} / 10.00**, adding up to **{total_score_needed:.0f} points**."
            )
        else:
            st.info("⚠️ Your expected average must be higher than your target to calculate realistically.")

    except Exception as e:
        st.error(f"❌ Error reading your CSV: {e}")

else:
    st.info("📂 Upload your CSV to get started.")

st.markdown(
    """
    <br><br>
    <sub>Made by Erwan Decotte</sub>
    """,
    unsafe_allow_html=True
)
