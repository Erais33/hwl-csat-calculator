import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
from collections import Counter

# ---- STYLE ----
st.markdown("""
<style>
html, body, .stApp { background-color: #F5F7FA; color: #002F4B; }
.block-container { background-color: #FFFFFF; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
input, .stDateInput input { background-color: #FFFFFF !important; color: #002F4B !important; }
.stNumberInput>div>div>input { background-color: #FFFFFF !important; color: #002F4B !important; }
.stButton>button { background-color: #F58220 !important; color: #FFFFFF !important; }
div[data-testid="stAlert-success"] { background-color: #E6F4EA !important; }
div[data-testid="stAlert-info"] { background-color: #E7F2FA !important; }
</style>
""", unsafe_allow_html=True)

# ---- LOGO ----
try:
    st.image("logohwl.png", width=200)
except:
    st.image("https://seeklogo.com/images/H/hostelworld-logo-57FDE8F7B1-seeklogo.com.png", width=200)

st.title("St Christopher's CSAT Insights Dashboard")

# ---- UPLOAD ----
st.header("📤 Upload Reviews CSV")
st.markdown("""
Upload a CSV with these columns: **Date**, **Ratings**, **Value For Money**, **Security**, **Location**, **Staff**, **Atmosphere**, **Cleanliness**, **Facilities**, **Comment**.
""")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # ---- SAFE LOAD ----
    df = pd.read_csv(
        uploaded_file,
        quotechar='"',
        on_bad_lines='skip',
        parse_dates=['Date'],
        dayfirst=True
    )
    st.success(f"✅ Loaded {len(df)} rows.")

    # ---- ROLLING WINDOW ----
    default_date = datetime.today().date()
    cutoff_date = st.date_input("📅 Forecast for date:", default_date)
    six_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=6)
    twelve_months_ago = pd.to_datetime(cutoff_date) - pd.DateOffset(months=12)

    rolling_df = df[(df['Date'] > six_months_ago) & (df['Date'] <= pd.to_datetime(cutoff_date))]
    rolling_reviews = len(rolling_df)
    current_avg = rolling_df['Ratings'].mean()

    st.subheader(f"📊 Current Rolling (Last 6 months)")
    st.write(f"Rolling reviews: {rolling_reviews} | Average: {current_avg:.2f} / 10.00")

    # ---- SUB-CATEGORIES ----
    subs = ['Value For Money', 'Security', 'Location', 'Staff', 'Atmosphere', 'Cleanliness', 'Facilities']
    st.subheader("🔍 Sub-Category Averages")

    sub_scores = {}
    for col in subs:
        avg = rolling_df[col].mean()
        sub_scores[col] = avg
        st.write(f"**{col}:** {avg:.2f} / 10.00")

    lowest_sub = min(sub_scores, key=sub_scores.get)
    st.info(f"💡 Focus tip: *{lowest_sub}* is your lowest sub-score at {sub_scores[lowest_sub]:.2f}. Focus here for best impact!")

    # ---- TREND CHART ----
    st.subheader("📈 Monthly CSAT Trend (Last 12 months)")
    trend_df = df[df['Date'] >= twelve_months_ago].copy()
    trend_df['Month'] = trend_df['Date'].dt.to_period('M')
    monthly_avg = trend_df.groupby('Month')['Ratings'].mean().reset_index()
    monthly_avg['Month'] = monthly_avg['Month'].dt.to_timestamp()

    fig, ax = plt.subplots()
    ax.plot(monthly_avg['Month'], monthly_avg['Ratings'], marker='o', color="#F58220")
    ax.set_title("Monthly Rolling CSAT")
    ax.set_ylabel("Average Rating")
    ax.set_ylim(0, 10)
    st.pyplot(fig)

    # ---- COMMENTS INSIGHTS ----
    st.subheader("📝 Comments Summary")
    all_comments = ' '.join(rolling_df['Comment'].dropna().astype(str)).lower()
    all_comments = re.sub(r'[^\w\s]', '', all_comments)  # remove punctuation
    words = all_comments.split()
    words = [w for w in words if len(w) > 2]  # drop tiny words

    word_counts = Counter(words)
    most_common = word_counts.most_common(10)

    st.write("**Most common words:**")
    st.write(', '.join([w for w, _ in most_common]))

    # ---- FORECAST ----
    st.header("🔮 CSAT Forecast")

    dropped_df = df[df['Date'] <= six_months_ago]
    dropped_reviews = len(dropped_df)
    drop_avg = dropped_df['Ratings'].mean() if dropped_reviews > 0 else 0.0

    base_reviews = rolling_reviews - dropped_reviews
    current_total = current_avg * rolling_reviews
    drop_total = drop_avg * dropped_reviews

    rolling_after_drop = current_total - drop_total
    base_reviews_remaining = max(base_reviews, 0)
    new_avg_if_none = (rolling_after_drop / base_reviews_remaining) if base_reviews_remaining > 0 else 0.0

    st.success(f"📉 If you add no new reviews, your rolling average would drop to: {new_avg_if_none:.2f} / 10.00")

    target_avg = st.number_input("🎯 Target rolling average:", value=9.0, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
    expected_new_avg = st.number_input("✅ Realistic average for new reviews:", value=9.2, min_value=0.1, max_value=10.0, step=0.1, format="%.2f")

    needed_points = target_avg * (base_reviews_remaining + 1) - rolling_after_drop

    if expected_new_avg > target_avg:
        new_reviews_needed = needed_points / (expected_new_avg - target_avg)
        new_reviews_needed = max(0, new_reviews_needed)
        total_score_needed = new_reviews_needed * expected_new_avg

        st.info(f"⭐️ To reach {target_avg:.2f}, you’d need about {new_reviews_needed:.0f} new reviews averaging {expected_new_avg:.2f} / 10.00 (total points needed: {total_score_needed:.0f}).")
    else:
        st.info("⚠️ Your expected average must be higher than your target to calculate realistically.")

    st.markdown("<br><br><sub>Made by Erwan Decotte</sub>", unsafe_allow_html=True)

else:
    st.info("📂 Upload your CSV to get your full CSAT insights forecast.")
