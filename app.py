import streamlit as st
import pandas as pd
from datetime import datetime

# 🎨 Page config
st.set_page_config(
    page_title="St Christopher's Inns • Rolling Average Tool",
    layout="centered"
)

# ✅ Better styling: visible text on white background
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #003366;
    }
    .stApp {
        background-color: #ffffff;
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #003366;
    }
    .stAlert, .stSuccess, .stWarning, .stInfo {
        border-left: 5px solid #003366;
        background-color: #f2f2f2; /* Soft grey for contrast */
        color: #003366;
    }
    .stButton>button {
        background-color: #003366;
        color: #ffffff;
    }
    .stNumberInput>div>input {
        background-color: #ffffff;
        color: #003366;
    }
    </style>
""", unsafe_allow_html=True)

# 🏨 App title
st.title("🏨 St Christopher's Inns • Rolling Average Forecast")

# 📖 Info block: explanation
st.info("""
### 📌 What is the Target Rolling Average?

Your rolling average is your average guest score over the last 6 months.
The **Target Rolling Average** is the score you'd like to reach next month.

This tool shows:
- If you add **no new reviews**, what your average might drop to.
- If you want to reach your target, how many reviews you’d need and what average those reviews must achieve.

Use this to plan improvements, staff training, or marketing campaigns.
""")

# 📂 File uploader
uploaded_file = st.file_uploader("📂 Upload your Hostelworld CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, on_bad_lines='skip')
        df['Ratings'] = pd.to_numeric(df['Ratings'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Ratings', 'Date'])

        current_reviews = len(df)
        current_avg = df['Ratings'].mean()

        st.write(f"✅ Loaded **{current_reviews} reviews** with an average score of **{current_avg:.2f}/10**")

        target_avg = st.number_input("🎯 Enter your Target Rolling Average", min_value=0.0, max_value=10.0, value=8.5, step=0.1)

        today = datetime.today()
        six_months_ago = today - pd.DateOffset(months=6)

        dropped_reviews = df[df['Date'] < six_months_ago]
        remaining_reviews = current_reviews - len(dropped_reviews)
        remaining_sum = df[df['Date'] >= six_months_ago]['Ratings'].sum()

        if remaining_reviews > 0:
            next_avg = remaining_sum / remaining_reviews
        else:
            next_avg = 0

        st.warning(f"⚠️ If you add no new reviews, your rolling average may drop to: **{next_avg:.2f}/10**")

        target_sum = target_avg * (remaining_reviews + 1)
        needed_sum = target_sum - remaining_sum

        if needed_sum <= 0:
            needed_reviews = 0
            needed_avg = 0.0
            st.success("🎉 Congratulations! You're already at or above your target.")
        else:
            needed_reviews = max(1, int(round(needed_sum / target_avg)))
            needed_avg = needed_sum / needed_reviews
            needed_avg = min(needed_avg, 10)

            st.success(
                f"⭐️ To reach your target average of **{target_avg:.2f}**, "
                f"you’d need **{needed_reviews} new reviews** with an average score of "
                f"**{needed_avg:.2f}/10**."
            )

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("📌 Please upload a CSV file to get started.")

st.caption("Made by Erwan Decotte • St Christopher's Inns")
