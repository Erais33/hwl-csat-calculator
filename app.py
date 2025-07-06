import streamlit as st
import pandas as pd
from datetime import datetime

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Rolling Average Forecast", layout="centered")

# ---- MODERN UI STYLING ----
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, .stApp {
        background-color: #F0F2F6;  /* Clean, light grey background */
        color: #1E1E1E;             /* Dark text for readability */
        font-family: 'Inter', sans-serif;
    }

    .st-emotion-cache-10trblm { /* Main title */
        color: #0068C9; /* Vibrant blue */
        font-weight: 700;
        text-align: center;
    }

    h2 { /* Headers */
        color: #0068C9; /* Vibrant blue */
        font-weight: 600;
        border-bottom: 2px solid #D1D9E4;
        padding-bottom: 8px;
    }
    
    .st-emotion-cache-z5fcl4 { /* Subheaders */
        background-color: rgba(0, 104, 201, 0.1);
        border-left: 5px solid #0068C9;
        padding: 1rem;
        border-radius: 8px;
    }

    .stButton > button {
        background-color: #0068C9;
        color: #FFFFFF;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background-color: #0052A1;
    }

    .stTextInput > div > div > input,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #D1D9E4;
    }
    
    div[data-testid="stMetric"], .st-emotion-cache-z5fcl4 {
        background-color: #FFFFFF;
        border: 1px solid #D1D9E4;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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

        st.subheader("🔍 Current Reviews Summary")
        col1, col2 = st.columns(2)
        col1.metric("Staying Reviews", f"{current_reviews_count}", f"Avg: {current_avg:.2f}")
        col2.metric("Dropping Reviews", f"{len(dropping_reviews_df)}", f"Avg: {dropping_reviews_df['Ratings'].mean():.2f}")

        # ---- SUBCATEGORY AVERAGES ----
        st.header("📊 Subcategory Averages")
        sub_cols = st.columns(3)
        categories = ["Value For Money", "Security", "Location", "Staff", "Atmosphere", "Cleanliness", "Facilities"]
        for i, col_name in enumerate(categories):
            with sub_cols[i % 3]:
                avg = current_reviews_df[col_name].mean() if not current_reviews_df.empty else 0.0
                st.metric(f"{col_name}", f"{avg:.2f}")

        # ---- TARGET & EXPECTED ----
        st.header("🎯 Forecast Inputs")
        input_col1, input_col2 = st.columns(2)
        with input_col1:
            target_avg = st.number_input(
                "Target rolling average:",
                value=9.0, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            )
        with input_col2:
            expected_new_avg = st.number_input(
                "Expected average for new reviews:",
                value=9.2, min_value=0.1, max_value=10.0, step=0.1, format="%.2f"
            )

        # ---- CALCULATE ----
        dropped_reviews_avg = dropping_reviews_df["Ratings"].mean() if not dropping_reviews_df.empty else 0.0
        dropped_reviews_count = len(dropping_reviews_df)
        
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
        if new_reviews_needed > 0 and expected_new_avg > target_avg:
             st.success(
                 f"To reach **{target_avg:.2f}**, you need about **{new_reviews_needed:.0f}** new reviews "
                 f"averaging **{expected_new_avg:.2f}**."
             )
        else:
             st.warning("Your 'Expected average' must be higher than your 'Target average' for this to work.")
        
        st.info(f"If you get no new reviews, your average will drop to **{new_avg_if_none:.2f}**.")


    except Exception as e:
        st.error(f"❌ Error reading or processing the CSV file: {e}")

else:
    st.info("📂 Upload your CSV file to get started.")

st.write("---")
st.caption("Made by Erwan Decotte")
