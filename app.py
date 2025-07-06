import streamlit as st
import pandas as pd
from datetime import datetime

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Rolling Average Forecast", layout="centered")

# ---- SIMPLE STYLE: SOFT ORANGE BACKGROUND ----
import streamlit as st

st.markdown(
    """
    <style>
    /* General Styles */
    html, body, .stApp {
        background-color: #1E1E1E;  /* Dark background for a modern look */
        color: #F5F5F5;             /* Soft white text for high contrast */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Professional font */
    }

    /* Main content area */
    .block-container {
        background-color: #2E2E2E;  /* Slightly lighter dark shade for content */
        border-radius: 10px;        /* Rounded corners for a softer feel */
        padding: 2rem;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
    }

    /* Headings and Text */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;             /* Pure white for prominent headings */
    }

    p, div, span, label {
        color: #F5F5F5 !important;   /* Ensures all text is consistently styled */
    }

    /* Input Widgets */
    input, .stDateInput input, .stTimeInput input {
        background-color: #3C3C3C !important; /* Darker input fields */
        color: #F5F5F5 !important;
        border: 1px solid #555555 !important; /* Subtle border */
        border-radius: 5px;         /* Rounded corners for inputs */
    }
    
    .stNumberInput > div > div > input {
        background-color: #3C3C3C !important;
        color: #F5F5F5 !important;
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #007BFF;  /* Dashed blue border to attract attention */
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 1rem;
    }

    .stFileUploader label {
        color: #007BFF !important;   /* Blue text to match the border */
        font-weight: bold;
    }

    /* Buttons */
    .stButton > button {
        background-color: #007BFF !important; /* Vibrant blue for primary actions */
        color: #FFFFFF !important;
        border-radius: 5px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: background-color 0.3s ease; /* Smooth hover effect */
    }
    
    .stButton > button:hover {
        background-color: #0056b3 !important; /* Darker blue on hover */
    }

    /* Alert and Message Boxes */
    div[data-testid="stAlert"] {
        background-color: #3C3C3C !important;
        color: #F5F5F5 !important;
        border-left: 5px solid #007BFF !important; /* Blue accent line */
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Example of how the styled elements will look
st.title("Modern UI for Streamlit")
st.write("This is an example of the new, improved styling for your application.")

st.number_input("Enter a number:")
st.text_input("Enter some text:")
st.file_uploader("Upload a file to see the new style:")
st.button("Submit")

st.info("This is an informational message with the new custom styling.")


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
