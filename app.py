import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Rolling Average Forecast", layout="centered")

# --- PROFESSIONAL UI STYLING ---
st.markdown("""
<style>
    /* --- Base & Background --- */
    html, body, .stApp {
        background: linear-gradient(180deg, #232834 0%, #2E3440 100%);
        color: #ECEFF4; /* Soft off-white for text */
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* --- Typography --- */
    /* Main title */
    .st-emotion-cache-10trblm {
        color: #ECEFF4; /* Main title in clean white */
        text-align: center;
        font-weight: 700;
    }
    
    /* General text */
    p, .st-emotion-cache-1c7y2kd {
        color: #D8DEE9; /* Slightly dimmer white for paragraphs */
    }

    /* Target specific headers to be orange */
    h2 {
        color: #FF7A2A !important; /* Rich accent orange */
        border-bottom: 2px solid #3B4252;
        padding-bottom: 10px;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Ensure subheaders and other text are NOT orange */
    h3, strong {
        color: #E5E9F0; /* Brighter white for emphasis */
    }

    /* --- Widgets & Inputs --- */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #3B4252; /* Dark slate for inputs */
        color: #ECEFF4;
        border-radius: 8px;
        border: 1px solid #4C566A;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stNumberInput, .stDateInput, .stTextInput {
        margin-bottom: 1rem;
    }

    /* --- Buttons --- */
    .stButton > button {
        background-color: #FF7A2A;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 10px rgba(255, 122, 42, 0.2);
    }
    .stButton > button:hover {
        background-color: #FFFFFF;
        color: #FF7A2A;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }

    /* --- File Uploader --- */
    .stFileUploader {
        border: 2px dashed #4C566A;
        background-color: rgba(76, 86, 106, 0.3);
        border-radius: 10px;
        padding: 1.5rem;
    }
    .stFileUploader label {
        color: #88C0D0; /* Icy blue for uploader label */
        font-weight: 600;
    }

    /* --- Info & Success Boxes --- */
    div[data-testid="stInfo"] {
        background-color: rgba(136, 192, 208, 0.1);
        border-left: 5px solid #88C0D0;
    }
    div[data-testid="stSuccess"] {
        background-color: rgba(163, 190, 140, 0.1);
        border-left: 5px solid #A3BE8C;
        color: #A3BE8C;
    }
    
    /* --- Separator & Caption --- */
    hr {
        border-top: 1px solid #3B4252;
    }
    .st-emotion-cache-1b0udgb {
        color: #4C566A;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


st.title("📊 Rolling Average Forecast")

# ---- UPLOAD ----
# This header is an h2, but we use st.subheader which renders as h3 to keep it white
st.subheader("📤 Upload your Hostelworld CSV")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

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

        st.success(f"✅ File uploaded successfully with {len(df)} rows.")

        df["Ratings"] = pd.to_numeric(df["Ratings"], errors='coerce')
        valid_reviews = df.dropna(subset=["Ratings", "Date"])

        # ---- FORECAST DATE ----
        st.header("📅 Forecast Date")
        st.write("Select a date to calculate the 6-month rolling average. Reviews older than 6 months from this date will be dropped.")

        default_date = datetime.today().date()
        cutoff_date = st.date_input("Forecast Cutoff Date:", default_date)

        six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)

        current_reviews_df = valid_reviews[
            (valid_reviews["Date"] > six_months_ago) & (valid_reviews["Date"] <= pd.to_datetime(cutoff_date))
        ]
        dropping_reviews_df = valid_reviews[valid_reviews["Date"] <= six_months_ago]

        current_avg = current_reviews_df["Ratings"].mean() if not current_reviews_df.empty else 0.0
        current_reviews_count = len(current_reviews_df)

        # ---- FORECAST INPUTS ----
        st.header("🎯 Forecast Inputs")
        
        col1, col2 = st.columns(2)
        with col1:
            target_avg = st.number_input(
                "Target Rolling Average:", value=9.0, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            )
        with col2:
            expected_new_avg = st.number_input(
                "Expected New Review Average:", value=9.2, min_value=0.1, max_value=10.0, step=0.1, format="%.2f"
            )

        # ---- CALCULATION ----
        current_total = current_avg * current_reviews_count
        base_reviews_remaining = len(current_reviews_df[current_reviews_df['Date'] > six_months_ago])
        rolling_total_after_drop = current_reviews_df[current_reviews_df['Date'] > six_months_ago]['Ratings'].sum()
        
        needed_total_points = target_avg * (base_reviews_remaining + 1) # Target for N+1 reviews
        points_to_gain = needed_total_points - rolling_total_after_drop
        
        new_reviews_needed = 0
        if expected_new_avg > target_avg:
            # Each new review adds (expected_new_avg - target_avg) to the 'surplus'
            new_reviews_needed = points_to_gain / (expected_new_avg - target_avg)
            new_reviews_needed = max(0, new_reviews_needed)

        new_avg_if_none = (
            rolling_total_after_drop / base_reviews_remaining if base_reviews_remaining > 0 else 0.0
        )
        
        # ---- SUBCATEGORY AVERAGES ----
        st.header("📊 Subcategory Averages")
        st.write("Current 6-month average for each category:")
        
        subcat_cols = ["Value For Money", "Security", "Location", "Staff",
                       "Atmosphere", "Cleanliness", "Facilities"]
        avg_ratings = {}
        for col in subcat_cols:
             avg_ratings[col] = current_reviews_df[col].mean() if not current_reviews_df.empty else 0.0
        
        # Display in three columns for a cleaner layout
        cat_col1, cat_col2, cat_col3 = st.columns(3)
        cols_list = [cat_col1, cat_col2, cat_col3]
        for i, (cat, avg) in enumerate(avg_ratings.items()):
            with cols_list[i % 3]:
                st.metric(label=cat, value=f"{avg:.2f}")


        # ---- FORECAST RESULTS ----
        st.header("📈 Forecast Results")

        st.metric(
            label="Predicted Average (with no new reviews)",
            value=f"{new_avg_if_none:.2f}",
            delta=f"{new_avg_if_none - current_avg:.2f} vs. current",
            delta_color="inverse"
        )
        
        if expected_new_avg <= target_avg:
            st.warning("Your 'Expected New Review Average' must be higher than your target to make progress.")
        else:
            st.success(
                f"To reach your target of **{target_avg:.2f}**, you need approximately "
                f"**{new_reviews_needed:.0f}** new reviews averaging **{expected_new_avg:.2f}**."
            )

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")

else:
    st.info("📂 Please upload your Hostelworld CSV file to begin the forecast.")

st.write("---")
st.caption("Made by Erwan Decotte")
