import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# --- Page setup ---
st.set_page_config(page_title="Hostelworld CSAT Forecast", layout="wide")
st.title("🏨 Hostelworld 6-Month Rolling CSAT Forecast Calculator")

# --- File uploader ---
uploaded_file = st.file_uploader("📂 Upload your Hostelworld CSV file (raw export)", type=['csv'])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            engine='python',  # More robust for messy CSVs
            on_bad_lines='warn'  # Warn about malformed lines but keep going
        )
        st.success(f"✅ Loaded {len(df)} rows")
    except Exception as e:
        st.error(f"❌ CSV read failed: {e}")
        st.stop()

    # --- Basic checks ---
    st.write("📋 Columns found:", df.columns.tolist())
    if "Ratings" not in df.columns:
        st.error("❌ Missing 'Ratings' column — please check your export.")
        st.stop()

    # --- Rolling average ---
    ratings = pd.to_numeric(df["Ratings"], errors='coerce').dropna()
    current_avg = ratings.mean()
    num_reviews = len(ratings)

    st.header("Current Rolling Average")
    st.write(f"⭐️ Current 6-month average rating: **{current_avg:.2f}** from {num_reviews} reviews")

    # --- Forecast inputs ---
    st.subheader("📈 Forecast next month")
    target_avg = st.number_input(
        "🎯 Target rolling average you want to reach",
        min_value=0.0, max_value=10.0, step=0.1
    )

    if target_avg > 0:
        # Calculate needed sum
        total_current_score = ratings.sum()
        needed_total_score = target_avg * (num_reviews + 1)

        needed_new_total_score = target_avg * (num_reviews + 1) - total_current_score

        # How many new reviews needed if they get your desired new review average
        new_review_avg = st.number_input(
            "Expected average score for your new reviews",
            min_value=0.0, max_value=10.0, step=0.1, value=9.5
        )

        if new_review_avg > 0:
            needed_reviews = (target_avg * (num_reviews + 1) - total_current_score) / new_review_avg
            needed_reviews = max(0, needed_reviews)
            st.write(f"➡️ To reach **{target_avg:.2f}**, you’d need about **{needed_reviews:.0f}** new reviews averaging **{new_review_avg:.2f}**")

        # No new reviews forecast
        rolling_drop = (total_current_score) / (num_reviews + 1)
        st.info(f"📉 If you add no new reviews, your rolling average will drop to ~**{rolling_drop:.2f}**")

    # --- Sub-category averages ---
    st.subheader("🔍 Sub-Category Averages")

    for cat in ["Value For Money", "Security", "Location", "Staff", "Atmosphere", "Cleanliness", "Facilities"]:
        if cat in df.columns:
            cat_ratings = pd.to_numeric(df[cat], errors='coerce').dropna()
            st.write(f"**{cat}**: {cat_ratings.mean():.2f}")

    # --- Basic comment summary ---
    if "Comment" in df.columns:
        comments = df["Comment"].dropna().astype(str).tolist()
        words = " ".join(comments).lower().split()
        word_counts = Counter(words)
        common_words = word_counts.most_common(15)
        st.subheader("💬 Comment Trends (simple word frequency)")
        for word, count in common_words:
            st.write(f"{word}: {count}")
    else:
        st.info("No 'Comment' column found.")

else:
    st.info("⬆️ Upload a raw Hostelworld CSV export to get started.")

st.caption("Made by Erwan Decotte")
