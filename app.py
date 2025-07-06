import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

# Safe NLTK usage
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    NLTK_READY = True
except Exception:
    NLTK_READY = False

st.set_page_config(page_title="Hostelworld CSAT Calculator", layout="wide")

st.title("🏨 Hostelworld 6-Month Rolling CSAT Calculator")

st.write("""
Upload your reviews CSV file.  
This app will:
- Keep **all rows**, even if some columns (like Comments) are missing
- Calculate rolling averages, forecast drops, and how many reviews + what average you need to hit your target
- Highlight your lowest sub-scores
- Give you a word summary of what guests are saying
""")

uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file:
    try:
        # Read with strict mode: no skip, no engine fallback
        df = pd.read_csv(uploaded_file, quotechar='"', keep_default_na=True)
        st.success(f"✅ Loaded {len(df)} rows.")
    except pd.errors.ParserError as e:
        st.error(f"❌ CSV ParserError: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        st.stop()

    # Check numeric column
    if "Ratings" not in df.columns:
        st.error("❌ The 'Ratings' column is missing!")
        st.stop()

    # Always works, even if some rows have NaN
    ratings = pd.to_numeric(df["Ratings"], errors="coerce").dropna()
    current_avg = ratings.mean()
    current_count = len(ratings)

    st.write(f"**Current rolling average:** {current_avg:.2f} over {current_count} reviews.")

    st.header("🎯 Rolling Target Forecast")

    col1, col2, col3 = st.columns(3)

    with col1:
        target_avg = st.number_input("Target rolling average", 0.0, 10.0, 8.5)
    with col2:
        reviews_dropping = st.number_input("Reviews dropping off next month", 0, current_count, 5)
    with col3:
        drop_avg = st.number_input("Average of dropped reviews", 0.0, 10.0, round(current_avg, 2))

    st.info("""
    **What is the Target Rolling Average?**
    This is the **total 6-month average you want next month**, after older reviews drop off & new ones are added.
    """)

    # Drop off effect
    total_now = current_avg * current_count
    total_minus_drop = total_now - (drop_avg * reviews_dropping)
    new_base = current_count - reviews_dropping

    if new_base > 0:
        drop_only = total_minus_drop / new_base
        st.warning(f"If you add no new reviews, your rolling average would drop to **{drop_only:.2f}**.")
    else:
        st.warning("All reviews would drop off. No base left!")

    # Calculate needed new reviews and required avg
    needed_reviews = None
    needed_avg = None
    for new_r in range(1, 500):
        total_reviews = new_base + new_r
        target_total = target_avg * total_reviews
        required_new_sum = target_total - total_minus_drop
        avg_needed = required_new_sum / new_r
        if 0 <= avg_needed <= 10:
            needed_reviews = new_r
            needed_avg = avg_needed
            break

    if needed_reviews:
        st.success(f"⭐️ To reach **{target_avg:.2f}**, you’d need **{needed_reviews} new reviews** "
                   f"with an average of **{needed_avg:.2f} / 10**.")
    else:
        st.error("🚫 No realistic way to reach that target. Try a lower goal.")

    st.header("📊 Sub-Category Averages")
    sub_cats = ['Value For Money', 'Security', 'Location', 'Staff', 'Atmosphere', 'Cleanliness', 'Facilities']
    sub_avgs = []
    for cat in sub_cats:
        if cat in df.columns:
            avg = pd.to_numeric(df[cat], errors="coerce").dropna().mean()
            st.write(f"**{cat}: {avg:.2f}**")
            sub_avgs.append((cat, avg))
    if sub_avgs:
        lowest = min(sub_avgs, key=lambda x: x[1])
        st.info(f"👉 Lowest sub-score: **{lowest[0]}** ({lowest[1]:.2f}). Focus here for best improvement!")

    st.header("📝 Guest Comments Summary")
    if 'Comment' in df.columns and NLTK_READY:
        all_comments = " ".join(str(c) for c in df['Comment'].dropna() if isinstance(c, str))
        if all_comments:
            words = word_tokenize(all_comments.lower())
            stops = set(stopwords.words('english'))
            keywords = [w for w in words if w.isalpha() and w not in stops]
            common_words = Counter(keywords).most_common(10)
            st.write("Most common guest keywords:", ", ".join(w for w, _ in common_words))
        else:
            st.info("No comments available to summarise.")
    else:
        st.info("No comment column found or NLTK not ready.")

    st.caption("✅ Made by Erwan Decotte")
else:
    st.info("Please upload your CSV to begin.")
