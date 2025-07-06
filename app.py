import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

# Try to import nltk safely
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    NLTK_READY = True
except Exception:
    NLTK_READY = False

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Hostelworld CSAT Calculator",
    layout="wide"
)

st.title("🏨 Hostelworld 6-Month Rolling CSAT Calculator")
st.markdown("""
Upload your CSV file of reviews.  
This tool helps you understand:
- **Your current rolling average score**
- How your score changes when reviews drop off
- How many new reviews you need next month to hit your target
- What average your new reviews must achieve  
""")

# ----------------------------
# Upload file
# ----------------------------
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Ratings" in df.columns:
        ratings = df["Ratings"].dropna().astype(float)
        current_avg = ratings.mean()
        current_count = len(ratings)
        st.success(f"✅ Found {current_count} reviews with average: **{current_avg:.2f}**")

        # Inputs
        st.header("🎯 Target & Drop-off")
        col1, col2 = st.columns(2)

        with col1:
            target_avg = st.number_input("Your target rolling average (after next month)", 0.0, 10.0, value=8.1)
        with col2:
            reviews_dropping = st.number_input("Reviews dropping off next month", 0, current_count, value=5)
            dropped_avg = st.number_input("Average score of dropped reviews", 0.0, 10.0, value=round(current_avg, 2))

        st.info("""
        **ℹ️ Target Rolling Average**  
        This is what you want your 6-month average to be **after next month** — once older reviews roll off and your new reviews are added.
        """)

        # Drop-off calculation
        total_now = current_avg * current_count
        drop_score = dropped_avg * reviews_dropping
        adjusted_total = total_now - drop_score
        new_base = current_count - reviews_dropping

        if new_base > 0:
            drop_only = adjusted_total / new_base
            st.warning(f"If you add **no** new reviews, your rolling average will drop to: **{drop_only:.2f}**")
        else:
            st.error("No reviews remain after drop-off. Check your inputs!")

        # Reviews needed for target
        needed_reviews = None
        needed_avg = None

        for new_r in range(1, 500):
            total_reviews = new_base + new_r
            target_total = target_avg * total_reviews
            required_new = target_total - adjusted_total
            avg_needed = required_new / new_r
            if 0 <= avg_needed <= 10:
                needed_reviews = new_r
                needed_avg = avg_needed
                break

        if needed_reviews:
            st.success(f"⭐️ To reach **{target_avg:.2f}**, you’d need **{needed_reviews} new reviews** "
                       f"with an average of **{needed_avg:.2f} / 10.00**.")
        else:
            st.error("🚫 No realistic scenario found with current input.")

        # ----------------------------
        # Sub-categories
        # ----------------------------
        st.header("📊 Sub-Category Averages")
        sub_cats = ['Value For Money', 'Security', 'Location', 'Staff', 'Atmosphere', 'Cleanliness', 'Facilities']
        sub_avgs = []
        for cat in sub_cats:
            if cat in df.columns:
                avg = df[cat].dropna().astype(float).mean()
                st.write(f"**{cat}: {avg:.2f}**")
                sub_avgs.append((cat, avg))

        if sub_avgs:
            lowest = min(sub_avgs, key=lambda x: x[1])
            st.info(f"👉 Focus for improvement: **{lowest[0]}: {lowest[1]:.2f}**")

        # ----------------------------
        # Comments summary
        # ----------------------------
        st.header("📝 Comments Summary")
        if 'Comment' in df.columns and NLTK_READY:
            all_text = " ".join(str(c) for c in df['Comment'].dropna())
            words = word_tokenize(all_text.lower())
            stops = set(stopwords.words('english'))
            keywords = [w for w in words if w.isalpha() and w not in stops]
            top_words = Counter(keywords).most_common(10)
            st.write("Most common words:", ", ".join([w for w, _ in top_words]))
        elif 'Comment' in df.columns:
            st.warning("⚠️ Install NLTK punkt & stopwords to summarise comments: "
                       "`import nltk; nltk.download('punkt'); nltk.download('stopwords')`")
        else:
            st.info("No comment data found.")

        st.divider()
        st.caption("✅ Made by Erwan Decotte")

    else:
        st.error("❌ No 'Ratings' column found in your CSV.")
else:
    st.info("Upload your CSV file to get started!")
