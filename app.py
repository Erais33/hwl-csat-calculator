import streamlit as st
import pandas as pd

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="6-Month Rolling CSAT Calculator",
    page_icon="✅",
    layout="centered"
)

# ---- BETTER BACKGROUND CSS ----
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
        background-image: linear-gradient(180deg, #f0f2f6 0%, #ffffff 100%);
    }
    .block-container {
        padding: 2rem 2rem;
        border-radius: 12px;
        background-color: #ffffffaa;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- LOCAL LOGO WITH FALLBACK ----
try:
    st.image("logohwl.png", width=200)
except:
    st.image("https://seeklogo.com/images/H/hostelworld-logo-57FDE8F7B1-seeklogo.com.png", width=200)

st.title("6-Month Rolling CSAT Average Calculator")
st.markdown(
    """
    Upload your **CSV file** of the last 6 months' reviews  
    or enter your data manually. 📈  
    """
)

st.divider()

# ---- UPLOAD CSV ----
st.header("📤 Upload Reviews CSV")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, quotechar='"', on_bad_lines='skip')
        st.write("✅ File uploaded!")

        st.write(f"Total rows in raw file: **{len(df)}**")

        if "Ratings" in df.columns:
            # Show rows with missing or invalid Ratings
            st.write(f"Rows with empty Ratings: {df['Ratings'].isna().sum()}")
            non_numeric_mask = ~df["Ratings"].astype(str).str.replace('.', '', 1).str.isnumeric()
            st.write(f"Rows with non-numeric Ratings: {non_numeric_mask.sum()}")

            st.write("🔍 Example of rows with empty Ratings:")
            st.write(df[df["Ratings"].isna()].head(5))

            st.write("🔍 Example of rows with non-numeric Ratings:")
            st.write(df[non_numeric_mask].head(5))

            # Safely convert Ratings
            df["Ratings"] = pd.to_numeric(df["Ratings"], errors='coerce')
            valid_ratings = df["Ratings"].dropna()

            calculated_avg = valid_ratings.mean()
            calculated_count = len(valid_ratings)

            st.success(f"✅ Using {calculated_count} valid reviews with an average of {calculated_avg:.2f}")
        else:
            st.error("❌ Could not find a 'Ratings' column in your CSV.")
            calculated_avg = None
            calculated_count = None

    except Exception as e:
        st.error(f"❌ Error reading your CSV: {e}")
        calculated_avg = None
        calculated_count = None

else:
    calculated_avg = None
    calculated_count = None

st.divider()

# ---- INPUTS ----
st.header("📊 Current Metrics")

col1, col2 = st.columns(2)
with col1:
    current_avg = st.number_input(
        "Current 6-month average",
        value=round(calculated_avg, 2) if calculated_avg else 7.93
    )
    current_reviews = st.number_input(
        "Current number of reviews",
        value=calculated_count if calculated_count else 106
    )
with col2:
    target_avg = st.number_input("Target rolling average", value=8.1)

st.header("🔄 Reviews Rolling Off & New Ones")

col3, col4 = st.columns(2)
with col3:
    dropped_reviews = st.number_input("Reviews dropping next month", value=15)
    dropped_reviews_avg = st.number_input("Average of dropped reviews", value=7.93)
with col4:
    new_reviews = st.number_input("Estimated new reviews next month", value=15)

st.divider()

# ---- CALCULATIONS ----
current_total = current_avg * current_reviews
drop_total = dropped_reviews * dropped_reviews_avg
new_total_reviews = current_reviews - dropped_reviews + new_reviews
target_total = target_avg * new_total_reviews

needed_from_new = target_total - (current_total - drop_total)

if new_reviews > 0:
    required_new_avg = needed_from_new / new_reviews
else:
    required_new_avg = 0

# ---- RESULTS ----
st.success(f"✅ **Your new reviews need to average:** `{required_new_avg:.2f}`")
st.info(f"New rolling total reviews: `{new_total_reviews}`")

# ---- FOOTER ----
st.markdown(
    """
    <br><br>
    <sub>Made with ❤️ for Hostelworld.</sub>
    """,
    unsafe_allow_html=True
)
