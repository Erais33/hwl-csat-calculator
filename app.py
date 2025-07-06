import streamlit as st
import pandas as pd
from datetime import datetime

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Rolling Average Forecast", layout="centered")

# ---- SIMPLE STYLE: SOFT ORANGE BACKGROUND ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #FFE5B4;  /* Light orange background */
        color: #111111;             /* Dark text for good contrast */
        font-family: Arial, sans-serif;
    }

    .block-container {
        background-color: #FFE5B4;  /* Orange main container */
        padding: 2rem;
    }

    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #111111 !important;  /* Ensure text is dark for readability */
    }

    input, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 1px solid #444444 !important;
    }

    .stNumberInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
    }

    /* Uploader text white for dark uploader box */
    .stFileUploader {
        color: #FFFFFF !important;
    }
    .stFileUploader label {
        color: #FFFFFF !important;
    }
    .stFileUploader div {
        color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #FF7F50 !important;  /* Coral button */
        color: #FFFFFF !important;             /* White text on buttons */
    }

    /* Messages and results with no colored boxes */
    div[data-testid="stAlert"] {
        background-color: transparent !important;
        color: #111111 !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---- TITLE ----
st.title("📊 Rolling Average Forecast")

# ---- UPLOAD ----
st.header("📤 Upload your Hostelworld CSV")
uploaded_file = st.file_uploader(
    "Upload CSV file with Date, Ratings, and subcategory columns",
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            usecols=[
                "Date", "Ratings",
                "Value For Money", "Security", "Location",
                "Staff", "Atmosphere", "Cleanliness", "Facilities"
            ],
            parse_dates=["Date"],
            dayfirst=True,
            on_bad_lines='skip'
        )

        st.success(f"✅ Uploaded! Total rows: {len(df)}")

        df["Ratings"] = pd.to_numeric(df["Ratings"], errors='coerce')
        valid_reviews = df.dropna(subset=["Ratings", "Date"])

        st.write(f"Valid reviews: {len(valid_reviews)}")

        # ---- FORECAST DATE ----
        st.header("📅 Forecast Date")
        st.write(
            "Pick the date to see your rolling 6-month average. "
            "Older reviews will drop off on this date."
        )

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

        st.subheader("🔍 Current Reviews Summary")
        st.write(f"Staying reviews: {current_reviews_count} | Avg: {current_avg:.2f} / 10.00")
        st.write(f"Dropping reviews: {dropped_reviews_count} | Avg: {dropped_reviews_avg:.2f} / 10.00")

        # ---- SUBCATEGORY AVERAGES ----
        st.subheader("📊 Subcategory Averages")
        for col in [
            "Value For Money", "Security", "Location",
            "Staff", "Atmosphere", "Cleanliness", "Facilities"
        ]:
            avg = current_reviews_df[col].mean() if not current_reviews_df.empty else 0.0
            st.write(f"{col}: {avg:.2f} / 10.00")

        # ---- TARGET & EXPECTED ----
        st.header("🎯 Forecast Inputs")
        st.write("**Target rolling average:** The 6-month score you want to reach.")
        target_avg = st.number_input(
            "Target rolling average:",
            value=9.0, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )

        st.write("**Expected average for new reviews:** The realistic average score you expect from new reviews.")
        expected_new_avg = st.number_input(
            "Expected average for new reviews:",
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

        st.header("📈 Forecast Results")
        st.write(f"📉 If you add no new reviews, your rolling average may drop to: {new_avg_if_none:.2f} / 10.00")
        if new_reviews_needed > 0:
            st.write(
                f"⭐️ To reach {target_avg:.2f}, you’d need about {new_reviews_needed:.0f} new reviews "
                f"averaging {expected_new_avg:.2f} / 10.00."
            )
        else:
            st.write("⚠️ Your expected average must be higher than your target for this to work realistically.")

    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")

else:
    st.info("📂 Upload your CSV file to start.")

st.write("---")
st.caption("Made by Erwan Decotte")
