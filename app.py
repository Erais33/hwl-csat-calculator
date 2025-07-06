import streamlit as st
import pandas as pd

# --- Page setup ---
st.set_page_config(page_title="Hostelworld Rolling CSAT Forecast", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }
        .main {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 2rem;
            color: #222222;
        }
        h1, h2, h3 {
            color: #0d47a1;
        }
        .stButton>button {
            background-color: #0d47a1;
            color: white;
        }
        .stNumberInput>div>input {
            background-color: #ffffff;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🏨 Hostelworld CSAT Rolling Average Forecast")

# --- Upload CSV ---
uploaded_file = st.file_uploader("📂 Upload your Hostelworld CSV file (raw export)", type=['csv'])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            engine='python',
            on_bad_lines='skip'
        )
        st.success(f"✅ Loaded {len(df)} rows from file")
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
        st.stop()

    # --- Check for needed columns ---
    if "Ratings" not in df.columns:
        st.error("❌ 'Ratings' column not found in your CSV.")
        st.stop()

    # --- Calculate current rolling average ---
    ratings = pd.to_numeric(df["Ratings"], errors='coerce').dropna()
    num_reviews = len(ratings)
    current_avg = ratings.mean()

    st.header("⭐️ Current Rolling Average")
    st.write(f"Current rolling average: **{current_avg:.2f}** based on **{num_reviews}** reviews")

    # --- Forecast if no new reviews ---
    rolling_drop = (ratings.sum()) / (num_reviews + 1)
    st.info(f"📉 If you add no new reviews, your rolling average will drop to: **{rolling_drop:.2f}**")

    # --- Target input ---
    st.subheader("🎯 Forecast to Reach a Target Score")
    target_avg = st.number_input(
        "Enter your target rolling average",
        min_value=0.0, max_value=10.0, step=0.1, value=round(current_avg + 0.2, 1)
    )

    if target_avg > 0:
        total_current_score = ratings.sum()

        needed_total = target_avg * (num_reviews + 1)
        needed_new_total = needed_total - total_current_score

        if needed_new_total > 0:
            needed_reviews = needed_new_total / 10.0
            needed_reviews = int(needed_reviews) + 1 if needed_reviews % 1 > 0 else int(needed_reviews)
            needed_avg = needed_new_total / needed_reviews
            needed_avg = min(needed_avg, 10.0)

            st.success(
                f"✅ To reach **{target_avg:.2f}**, you need about **{needed_reviews} new reviews** "
                f"averaging **{needed_avg:.2f} / 10.0**."
            )
        else:
            st.success("✅ You’ve already reached your target!")

else:
    st.info("⬆️ Upload your CSV file above to get started.")

st.caption("Made by Erwan Decotte")
st.markdown('</div>', unsafe_allow_html=True)
