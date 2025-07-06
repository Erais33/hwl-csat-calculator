import streamlit as st
import pandas as pd
from datetime import datetime

# ---- STYLE ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #F58220; /* St Christopher’s orange */
        color: #000000; /* All text black */
    }
    .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    input, .stDateInput input, .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    .stButton>button {
        background-color: #002F4B !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        padding: 1em !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
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
st.header("📤 Upload Hostelworld CSV")
uploaded_file = st.file_uploader("Upload your Hostelworld CSV file", type=["csv"])

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

        st.write(f"✅ File uploaded! Total rows: {len(df)}")

        # Clean numeric
        for col in ["Ratings", "Value For Money", "Security", "Location",
                    "Staff", "Atmosphere", "Cleanliness", "Facilities"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        valid_reviews = df.dropna(subset=["Ratings", "Date"])
        st.write(f"Valid reviews: {len(valid_reviews)}")
        if len(valid_reviews) != len(df):
            st.warning(f"{len(df) - len(valid_reviews)} rows skipped due to missing data.")

        # ---- FORECAST DATE ----
        st.header("📅 Forecast Date")
        st.markdown(
            "📅 **Select forecast date:** Pick the date you want to see your rolling average forecast for. "
            "Older reviews than 6 months will drop off on that date."
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

        st.header("🧾 Summary")
        st.success(f"✅ Staying reviews: {current_reviews_count} | Avg: {current_avg:.2f} / 10.00")
        st.info(f"🔻 Dropping reviews: {dropped_reviews_count} | Avg: {dropped_reviews_avg:.2f} / 10.00")

        # ---- SUBCATEGORY AVERAGES ----
        st.header("📊 Subcategory Averages (Current 6 Months)")
        for col in ["Value For Money", "Security", "Location",
                    "Staff", "Atmosphere", "Cleanliness", "Facilities"]:
            avg = current_reviews_df[col].mean() if not current_reviews_df.empty else 0.0
            st.write(f"{col}: {avg:.2f} / 10.00")

        # ---- TARGET ----
        st.header("🎯 Set Your Target")
        st.markdown(
            """
            📖 **What is the Target Rolling Average?**  
            The Target Rolling Average is the score you want your hostel’s last 6-month guest rating to reach.

            This tool shows:
            - 📉 If you add no new reviews, what your rolling average may drop to.
            - ⭐️ If you want to hit your target, how many new reviews you’d need and what average they must score.

            Use this to plan improvements & forecast realistic scores!
            """
        )

        target_avg = st.number_input(
            "🎯 Target rolling average:",
            value=9.0, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
        )
        st.markdown(
            "🔢 **What is this?** Enter the score you want your last 6-month rolling average to be after older reviews drop."
        )

        expected_new_avg = st.number_input(
            "✍️ Expected average for new reviews:",
            value=9.2, min_value=0.1, max_value=10.0, step=0.1, format="%.2f"
        )
        st.markdown(
            "📝 **What is this?** Enter what you realistically expect new reviews will average based on improvements."
        )

        # ---- CALCULATE ----
        current_total = current_avg * current_reviews_count
        drop_total = dropped_reviews_avg * dropped_reviews_count
        rolling_total_after_drop = current_total - drop_total

        base_reviews_remaining = current_reviews_count - dropped_reviews_count
        if base_reviews_remaining < 0:
            base_reviews_remaining = 0

        needed_points_from_new = target_avg * (base_reviews_remaining + 1) - rolling_total_after_drop

        if expected_new_avg > target_avg and needed_points_from_new > 0:
            new_reviews_needed = needed_points_from_new / (expected_new_avg - target_avg)
            new_reviews_needed = max(0, new_reviews_needed)
        else:
            new_reviews_needed = 0

        new_avg_if_none = (
            rolling_total_after_drop / base_reviews_remaining if base_reviews_remaining > 0 else 0.0
        )

        # ---- RESULTS ----
        st.header("📈 Forecast")
        st.success(
            f"📉 If you add no new reviews, your rolling average would drop to: **{new_avg_if_none:.2f} / 10.00**"
        )
        if new_reviews_needed > 0:
            st.info(
                f"⭐️ To reach **{target_avg:.2f}**, you’d need about **{new_reviews_needed:.0f}** new reviews "
                f"averaging **{expected_new_avg:.2f} / 10.00**."
            )
        else:
            st.info("⚠️ Your expected average must be higher than your target to calculate realistically.")

    except Exception as e:
        st.error(f"❌ Error reading your CSV: {e}")
else:
    st.info("📂 Upload your Hostelworld CSV file to begin.")

st.markdown(
    "<br><sub>Made by Erwan Decotte</sub>",
    unsafe_allow_html=True
)
