import streamlit as st
import pandas as pd
from datetime import datetime

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Rolling Average Forecast", layout="centered")

# ---- HIGH-CONTRAST STYLING ----
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;700&display=swap');

    html, body, .stApp {
        background-color: #0D1117;  /* Deep navy background */
        color: #FFFFFF;             /* White text */
        font-family: 'Lexend', sans-serif;
    }

    /* Main title */
    .st-emotion-cache-10trblm {
        color: #39D3BB; /* Bright aqua accent */
        text-align: center;
        font-weight: 700;
    }

    /* Headers */
    h2 {
        color: #39D3BB; /* Bright aqua accent */
        font-weight: 600;
        border-bottom: 2px solid #21262D;
        padding-bottom: 10px;
    }
    
    /* Subheaders */
    h3 {
        color: #C9D1D9; /* Lighter grey for sub-titles */
    }

    /* Buttons */
    .stButton > button {
        background-color: #39D3BB;
        color: #0D1117; /* Dark text on button for contrast */
        border-radius: 8px;
        font-weight: 700;
        padding: 12px 24px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #A6FFF2;
    }

    /* Input Widgets */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #161B22; /* Slightly lighter navy for inputs */
        color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #30363D;
    }

    /* Alert Boxes (Success, Warning, Info) */
    div[data-testid="stSuccess"] {
        background-color: rgba(57, 211, 187, 0.1);
        border-left: 5px solid #39D3BB;
        color: #39D3BB;
    }
    div[data-testid="stWarning"] {
        background-color: rgba(255, 179, 6, 0.1);
        border-left: 5px solid #FFB306;
        color: #FFB306;
    }
     div[data-testid="stInfo"] {
        background-color: rgba(67, 133, 245, 0.1);
        border-left: 5px solid #4385F5;
        color: #4385F5;
    }
    
    /* Standard Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    /* Custom Summary Cards (without arrows) */
    .custom-summary-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: left; /* Align text to the left */
        height: 100%;
    }
    .custom-summary-label {
        color: #C9D1D9;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
    .custom-summary-value {
        color: #FFFFFF;
        font-size: 2.5rem;
        font-weight: 600;
        line-height: 1.2;
    }
    .custom-summary-avg {
        color: #C9D1D9;
        font-size: 1rem;
        margin-top: 0.25rem;
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
        with col1:
            st.markdown(f"""
            <div class="custom-summary-card">
                <div class="custom-summary-label">Staying Reviews</div>
                <div class="custom-summary-value">{current_reviews_count}</div>
                <div class="custom-summary-avg">Avg: {current_avg:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            dropping_avg = dropping_reviews_df['Ratings'].mean() if not dropping_reviews_df.empty else 0.0
            st.markdown(f"""
            <div class="custom-summary-card">
                <div class="custom-summary-label">Dropping Reviews</div>
                <div class="custom-summary-value">{len(dropping_reviews_df)}</div>
                <div class="custom-summary-avg">Avg: {dropping_avg:.2f}</div>
            </div>
            """, unsafe_allow_html=True)


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
