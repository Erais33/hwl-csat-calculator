import streamlit as st
import pandas as pd
from datetime import datetime

# ---- STYLE ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background: linear-gradient(to bottom, #FDE3CF, #ffffff);
        color: #000000;
    }

    .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        max-width: 1000px;
        margin: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    input, .stDateInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    label, div[data-testid="stDateInputLabel"], div[data-testid="stNumberInputLabel"], .stFileUploader label {
        color: #000000 !important;
    }

    div[data-testid="stAlert-success"], 
    div[data-testid="stAlert-info"], 
    div[data-testid="stAlert-warning"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- HEADER ----
st.title("📊 Hostelworld • Rolling Average Forecast")

# ---- UPLOAD ----
st.header("📤 Upload Reviews CSV")

uploaded_file = st.file_uploader(
    "Upload your Hostelworld CSV file for the last 6 months",  # ✅ This is the only label, keep it short
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            usecols=["Date", "Ratings", "Value For Money", "Security", "Location",
                     "Staff", "Atmosphere", "Cleanliness", "Facilities"],
            parse_dates=["Date"],
            dayfirst=True,
            on_bad_lines='skip'
        )
        st.write(f"✅ File uploaded! Total rows read: {len(df)}")

        df["Ratings"] = pd.to_numeric(df["Ratings"], errors='coerce')
        valid_df = df.dropna(subset=["Ratings", "Date"])
        st.write(f"Valid Ratings rows: {len(valid_df)}")

        # ---- 6-month calculation ----
        st.header("📅 Forecast Date")
        cutoff_date = st.date_input("Select forecast date:", datetime.today())
        six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)
        
        st.markdown(
    """
    📅 **What does this mean?**  
    The forecast date is the day you want to look ahead to.  
    Any reviews older than 6 months from this date will drop out of your rolling average.  
    Use it to see what will happen if you get no new reviews, or plan how many you’ll need to reach your goal.
    """
)


        current_df = valid_df[
            (valid_df["Date"] > six_months_ago) & (valid_df["Date"] <= pd.to_datetime(cutoff_date))
        ]
        dropping_df = valid_df[valid_df["Date"] <= six_months_ago]

        current_avg = current_df["Ratings"].mean() if not current_df.empty else 0.0
        current_count = len(current_df)

        dropping_avg = dropping_df["Ratings"].mean() if not dropping_df.empty else 0.0
        dropping_count = len(dropping_df)

        st.header("📊 Current & Dropping Reviews")
        st.write(f"✅ Staying reviews: {current_count} | Avg: {current_avg:.2f} / 10.00")
        st.write(f"🔻 Dropping reviews: {dropping_count} | Avg: {dropping_avg:.2f} / 10.00")

        # ---- Subcategory Averages ----
        st.header("🔍 Subcategory Averages")
        subcats = ["Value For Money", "Security", "Location",
                   "Staff", "Atmosphere", "Cleanliness", "Facilities"]
        for cat in subcats:
            avg = current_df[cat].mean() if cat in current_df else None
            if avg:
                st.write(f"**{cat}:** {avg:.2f} / 10.00")

        # ---- TARGET ----
        st.header("🎯 Set Your Target")
        st.markdown(
            """
            📖 **What is the Target Rolling Average?**

            The Target Rolling Average is the score you want your hostel’s last 6-month guest rating to reach.

            This tool shows:
            - 📉 If you add no new reviews, what your rolling average may drop to next month.
            - ⭐️ If you want to hit your target, how many new reviews you’d need and what average they must score.

            Use this to plan improvements & forecast realistic scores!
            """
        )

        target_avg = st.number_input("🎯 Target rolling average:", min_value=0.0, max_value=10.0, value=9.0, step=0.1)
        expected_new_avg = st.number_input("✍️ Expected average for new reviews:", min_value=0.1, max_value=10.0, value=9.2, step=0.1)

        # ---- Calculate ----
        base_total = current_avg * current_count
        drop_total = dropping_avg * dropping_count
        after_drop_total = base_total - drop_total
        base_remaining = current_count - dropping_count
        base_remaining = max(base_remaining, 0)

        if base_remaining > 0:
            no_new_avg = after_drop_total / base_remaining
        else:
            no_new_avg = 0.0

        needed_points = target_avg * (base_remaining + 1) - after_drop_total
        if expected_new_avg > target_avg:
            needed_reviews = needed_points / (expected_new_avg - target_avg)
        else:
            needed_reviews = 0

        needed_reviews = max(0, needed_reviews)

        st.header("📈 Forecast")
        st.write(f"📉 If you add no new reviews, your rolling average would drop to: **{no_new_avg:.2f} / 10.00**")
        if needed_reviews > 0:
            st.write(
                f"⭐️ To reach **{target_avg:.2f}**, you’d need about **{needed_reviews:.0f}** "
                f"new reviews averaging **{expected_new_avg:.2f} / 10.00**."
            )
        else:
            st.write("⚠️ Your expected average must be higher than your target to calculate realistically.")

    except Exception as e:
        st.error(f"❌ CSV Error: {e}")

else:
    st.write("📂 Please upload your Hostelworld CSV to start.")

st.markdown(
    """
    ---
    <sub>• Made by Erwan Decotte •</sub>
    """,
    unsafe_allow_html=True
)
