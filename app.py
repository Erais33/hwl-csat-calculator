import streamlit as st
import pandas as pd

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="6-Month Rolling CSAT Calculator",
    page_icon="✅",
    layout="centered"
)

# ---- RESET & BRAND COLORS ----
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #F9FAFB;
        color: #002F4B;
    }

    .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }

    h1, h2, h3, h4, h5, h6 {
        color: #002F4B;
    }

    .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #002F4B !important;
    }

    input {
        background-color: #FFFFFF !important;
        color: #002F4B !important;
    }

    .stButton>button {
        background-color: #F58220 !important;
        color: #FFFFFF !important;
        border: none;
        border-radius: 4px;
        padding: 0.5em 1em;
    }

    /* CUSTOM ALERT BOX STYLING */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        padding: 1em;
    }

    div[data-testid="stAlert-success"] {
        background-color: #DFF5E1 !important;
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

st.title("6-Month Rolling CSAT Average Calculator")

st.divider()

# ---- UPLOAD CSV ----
st.header("📤 Upload Reviews CSV")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(
            uploaded_file,
            usecols=["Ratings"],
            quotechar='"',
            on_bad_lines='skip'
        )
        st.write("✅ File uploaded!")

        st.write(f"Total rows read: {len(df)}")

        df["Ratings"] = pd.to_numeric(df["Ratings"], errors='coerce')
        valid_ratings = df["Ratings"].dropna()

        st.write(f"Valid Ratings rows: {len(valid_ratings)}")
        if len(valid_ratings) != len(df):
            st.warning(f"{len(df) - len(valid_ratings)} rows skipped (empty or invalid).")

        calculated_avg = valid_ratings.mean()
        calculated_count = len(valid_ratings)

        st.success(f"✅ Found {calculated_count} valid reviews with an average score of {calculated_avg:.2f}")

    except Exception as e:
        st.error(f"❌ There was an error reading your CSV: {e}")
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
st.success(f"✅ Your new reviews need to average: {required_new_avg:.2f}")
st.info(f"New rolling total reviews: {new_total_reviews}")

# ---- FOOTER ----
st.markdown(
    """
    <br><br>
    <sub>Made by Erwan Decotte.</sub>
    """,
    unsafe_allow_html=True
)
