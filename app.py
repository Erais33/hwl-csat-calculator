import streamlit as st
import pandas as pd
from datetime import datetime

# ---- PAGE STYLE ----
st.set_page_config(page_title="St Christopher's Inns • Rolling Average Forecast", layout="centered")

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
st.title("📊 St Christopher's Inns • Rolling Average Forecast")

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
            st.write(f"- **{col}**: {avg:.2f}
