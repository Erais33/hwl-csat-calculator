import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import nltk

# Download punkt for tokenizing (one time)
nltk.download('punkt')
from nltk.tokenize import word_tokenize

st.set_page_config(
    page_title="Hostelworld CSAT Rolling Average",
    layout="wide"
)

st.title("🏨 Hostelworld 6-Month Rolling CSAT Calculator")

st.write("""
Upload your last 6 months reviews CSV. 
We'll calculate your current rolling average, show how it drops if you do nothing, 
and help you see what you need to reach your Month +1 target!
""")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Assure Dates are parsed
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    else:
        st.error("❌ Could not find a 'Date' column.")
    
    if 'Ratings' in df.columns:
        valid_ratings = df['Ratings'].dropna().astype(float)
        calculated_avg = valid_ratings.mean()
        calculated_count = len(valid_ratings)
        st.success(f"✅ Found {calculated_count} reviews with an average score of {calculated_avg:.2f}")

        # Current metrics inputs
        st.header("📊 Current Metrics")

        col1, col2 = st.columns(2)
        with col1:
            current_avg = st.number_input("Current 6-month rolling average", 0.0, 10.0, value=calculated_avg, step=0.01)
            current_reviews = st.number_input("Current number of reviews", 0, 10000, value=calculated_count, step=1)
        with col2:
            target_avg = st.number_input("🎯 Target rolling average for Month +1", 0.0, 10.0, value=8.1, step=0.01)
        
        st.markdown("""
        **What does this mean?**  
        The *target rolling average* is what you want your **new 6-month average** to be **AFTER next month**, once older reviews roll off and new ones come in.
        """)

        st.header("🔄 Rolling Changes")

        col1, col2 = st.columns(2)
        with col1:
            reviews_dropping = st.number_input("Reviews dropping next month", 0, current_reviews, value=5, step=1)
            dropped_avg = st.number_input("Average of dropped reviews", 0.0, 10.0, value=current_avg, step=0.01)
        
        # Drop-off calculation
        total_score_now = current_avg * current_reviews
        score_dropping = dropped_avg * reviews_dropping
        adjusted_total = total_score_now - score_dropping
        new_review_base = current_reviews - reviews_dropping

        if new_review_base > 0:
            if_no_new_reviews = adjusted_total / new_review_base
            st.info(f"If you add no new reviews, your rolling average will drop to: **{if_no_new_reviews:.2f}**")
        else:
            st.warning("No base reviews remaining. Check your numbers!")

        # Needed new reviews calculation (find possible counts that make sense)
        needed_reviews = None
        needed_avg = None

        for new_reviews in range(1, 300):
            new_total_reviews = new_review_base + new_reviews
            target_total_score = target_avg * new_total_reviews
            required_new_score = target_total_score - adjusted_total
            avg_for_new_reviews = required_new_score / new_reviews

            if 0 <= avg_for_new_reviews <= 10:
                needed_reviews = new_reviews
                needed_avg = avg_for_new_reviews
                break

        if needed_reviews:
            st.success(f"⭐️ To reach your Month +1 target of **{target_avg:.2f}**, "
                       f"you’d need **{needed_reviews} new reviews** averaging "
                       f"**{needed_avg:.2f} / 10.00**.")
        else:
            st.warning("🚫 With your inputs, reaching the target isn't feasible. Try adjusting your target or dropping average.")

        st.divider()

        # Subcategory averages
        st.header("📊 Sub-category Averages")
        sub_cats = ['Value For Money', 'Security', 'Location', 'Staff', 'Atmosphere', 'Cleanliness', 'Facilities']
        sub_summaries = []
        for cat in sub_cats:
            if cat in df.columns:
                avg = df[cat].dropna().astype(float).mean()
                st.write(f"**{cat}: {avg:.2f}**")
                sub_summaries.append((cat, avg))

        lowest_sub = min(sub_summaries, key=lambda x: x[1]) if sub_summaries else None
        if lowest_sub:
            st.info(f"📌 Tip: Your lowest sub-score is **{lowest_sub[0]}: {lowest_sub[1]:.2f}**. Focus here for best improvement!")

        st.divider()

        # Comments summary
        st.header("📝 Comments Summary")
        if 'Comment' in df.columns:
            all_comments = " ".join(str(c) for c in df['Comment'].dropna() if isinstance(c, str))
            words = word_tokenize(all_comments.lower())
            stop_words = set(nltk.corpus.stopwords.words('english'))
            words_filtered = [w for w in words if w.isalpha() and w not in stop_words]
            word_freq = Counter(words_filtered)
            most_common = word_freq.most_common(10)
            good_trends = [w for w, freq in most_common if freq > 3]

            st.write("**Main trends in comments:**")
            st.write(", ".join(good_trends) if good_trends else "Not enough data for trends.")
        else:
            st.info("No 'Comment' column found to analyze trends.")

        st.markdown("----")
        st.markdown("✅ *Made by Erwan Decotte*")

    else:
        st.error("❌ Could not find a 'Ratings' column.")
else:
    st.info("📤 Upload your CSV file to begin.")
