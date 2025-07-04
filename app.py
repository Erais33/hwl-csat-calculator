import streamlit as st
import pandas as pd
from datetime import datetime

# ---- ST CHRISTOPHER'S INNS STYLE ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #F5F7FA;
        color: #002F4B;
    }

    .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    h1, h2, h3, h4, h5, h6 {
        color: #002F4B;
    }

    p, span, div {
        color: #002F4B;
    }

    input, .stDateInput input {
        background-color: #FFFFFF !important;
        color: #002F4B !important;
        border: 1px solid #002F4B !important;
    }

    .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #002F4B !important;
    }

    .stButton>button {
        background-color: #F58220 !important;
        color: #FFFFFF !important;
        border: none;
        border-radius: 5px;
        padding: 0.5em 1.2em;
    }

    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        padding: 1em !important;
    }

    div[data-testid="stAlert-success"] {
        background-color: #E6F4EA !important;
    }
    div[data-testid="stAlert-success"] p {
        color: #002F4B !important;
        font-weight: 600 !important;
    }

    div[data-testid="stAlert-info"] {
        background-color: #E7F2FA !important;
    }
    div[data-testid="stAlert-info"] p {
        color: #002F4B !important;
        font-weight: 600 !important;
    }

    div[data-testid="stAlert-error"] {
        background-color: #FDE2E2 !important;
    }
    div[data-testid="stAlert-error"] p {
        color: #002F4B !important;
        font-weight: 600 !important;
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

# ---- UPLOAD ----
st.header("📤 Upload Reviews CSV")
st.markdown("Upload a CSV file that includes **Date** and **Ratings** columns. Each row should have when the review was posted and its score (0–10).")

uploaded_file = st.file_uploader("Upload your CSV file (Date + Ratings)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            usecols=["Date", "Ratings"],
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

        # ---- DATE INPUT ----
        st.header("📅 Select Your Forecast Date")
        st.markdown(
            "Pick the date you want to forecast your rolling average for. "
            "For example, if you choose **5th July**, all reviews older than 6 months "
            "before that date will drop out of the calculation."
        )

        default_date = datetime.today().date()
        cutoff_date = st.date_input("Forecast for date:", default_date)

        six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)

        # Rolling window reviews
        current_reviews_df = valid_reviews[
            (valid_reviews["Date"] > six_months_ago) & (valid_reviews["Date"] <= pd.to_datetime(cutoff_date))
        ]
        dropping_reviews_df = valid_reviews[valid_reviews["Date"] <= six_months_ago]

        current_avg = current_reviews_df["Ratings"].mean() if not current_reviews_df.empty else 0.0
        current_reviews_count = len(current_reviews_df)

        dropped_reviews_count = len(dropping_reviews_df)
        dropped_reviews_avg = dropping_reviews_df["Ratings"].mean() if not dropping_reviews_df.empty else 0.0

        st.header("🧾 Summary")
        st.success(f"✅ **Reviews staying:** {current_reviews_count} | Average: {current_avg:.2f} / 10.00")
        st.info(f"🔻 **Reviews dropping off:** {dropped_reviews_count} | Average: {dropped_reviews_avg:.2f} / 10.00")

        # ---- TARGET ----
        st.header("🎯 Set Your Target")
        st.markdown(
            "Set the **rolling average score you want to reach** and how many new reviews you expect to get "
            "in that period. This shows what average those new reviews need to achieve."
        )

        target_avg = st.number_input(
            "Your target rolling average:",
            value=8.10, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )
        new_reviews = st.number_input(
            "Estimated new reviews next month:",
            value=0, min_value=0
        )

        # ---- CALCULATE FUTURE ----
        current_total = current_avg * current_reviews_count
        drop_total = dropped_reviews_avg * dropped_reviews_count
        new_total_reviews = current_reviews_count - dropped_reviews_count + new_reviews
        target_total = target_avg * new_total_reviews
        needed_from_new = target_total - (current_total - drop_total)

        if new_reviews > 0:
            required_new_avg = needed_from_new / new_reviews
            required_new_avg = min(required_new_avg, 10.0)
        else:
            required_new_avg = 0.0

        new_avg_if_none = (
            (current_total - drop_total) / new_total_reviews if new_total_reviews > 0 else 0.0
        )

        # ---- RESULTS ----
        st.header("📊 Forecast")
        st.success(
            f"📉 If you add no new reviews, your rolling average would drop to: **{new_avg_if_none:.2f} / 10.00**"
        )
        if new_reviews > 0:
            st.info(
                f"⭐️ To reach **{target_avg:.2f}**, you need **{new_reviews}** new reviews "
                f"with an average of **{required_new_avg:.2f} / 10.00**"
            )
        else:
            st.info("You haven't entered any new reviews to calculate a target average.")

    except Exception as e:
        st.error(f"❌ Error reading your CSV: {e}")
else:
    st.info("📂 Upload your CSV to begin your forecast.")

st.markdown(
    """
    <br><br>
    <sub>Made by Erwan Decotte</sub>
    """,
    unsafe_allow_html=True
)
