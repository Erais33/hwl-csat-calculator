import streamlit as st

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="6-Month Rolling CSAT Calculator",
    page_icon="✅",
    layout="centered"
)

# ---- HEADER WITH LOGO ----
st.image(
    "https://seeklogo.com/images/H/hostelworld-logo-57FDE8F7B1-seeklogo.com.png",
    width=200
)

st.title("6-Month Rolling CSAT Average Calculator")
st.markdown(
    """
    Use this tool to see what **average score** you need next month  
    to hit your target rolling CSAT. 📈  
    """
)

st.divider()

# ---- INPUTS ----
st.header("📊 Current Metrics")

col1, col2 = st.columns(2)
with col1:
    current_avg = st.number_input("Current 6-month average", value=7.93)
    current_reviews = st.number_input("Current number of reviews", value=106)
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
    <sub>Made Erwan Decotte.</sub>
    """,
    unsafe_allow_html=True
)
