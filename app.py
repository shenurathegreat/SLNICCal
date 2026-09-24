
from datetime import datetime
import streamlit as st

# Set up page config
st.set_page_config(page_title="NIC Details & Age Calculator", page_icon="📇", layout="centered")

# --- HELPER FUNCTIONS ---

def process_nic(nic_str):
    """Parses Sri Lankan NIC (Old 9+V/X or New 12-digit) for Gender, Year, and DOB."""
    nic_str = nic_str.strip().upper()
    
    # Standardize NIC length to extract Year and Day-of-Year
    if len(nic_str) == 10 and (nic_str[-1] in ['V', 'X']):
        # Old NIC: e.g., 951234567V -> Year: 1995, Days: 123
        year_int = int("19" + nic_str[:2])
        day_of_year = int(nic_str[2:5])
    elif len(nic_str) == 12 and nic_str.isdigit():
        # New NIC: e.g., 199512345678 -> Year: 1995, Days: 123
        year_int = int(nic_str[:4])
        day_of_year = int(nic_str[4:7])
    else:
        return None, "Invalid NIC format. Must be 9 digits + V/X or 12 digits."

    # Gender determination
    gender = "Female" if day_of_year > 500 else "Male"
    days = day_of_year - 500 if day_of_year > 500 else day_of_year

    # Day-of-Year to Month & Date Mapping (Non-leap year base)
    months = [
        ("January", 31, 1), ("February", 29, 2), ("March", 31, 3),
        ("April", 30, 4), ("May", 31, 5), ("June", 30, 6),
        ("July", 31, 7), ("August", 31, 8), ("September", 30, 9),
        ("October", 31, 10), ("November", 30, 11), ("December", 31, 12)
    ]

    month_name = ""
    month_num = 0
    date_of_birth = 0

    for m_name, m_days, m_num in months:
        if days <= m_days:
            month_name = m_name
            month_num = m_num
            date_of_birth = days
            break
        days -= m_days

    if not month_name:
        return None, "Invalid day sequence in NIC."

    # Construct Date Object
    dob_date = datetime(year_int, month_num, date_of_birth)

    return {
        "birth_year": str(year_int),
        "gender": gender,
        "month": month_name,
        "day": date_of_birth,
        "dob_date": dob_date
    }, None


def calculate_age(dob):
    """Calculates age in years, months, and days relative to current time."""
    today = datetime.now()
    
    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day

    if days < 0:
        months -= 1
        # Get previous month's total days
        prev_month = (today.month - 1) if today.month > 1 else 12
        prev_year = today.year if today.month > 1 else today.year - 1
        days += (datetime(prev_year, prev_month % 12 + 1, 1) - datetime(prev_year, prev_month, 1)).days

    if months < 0:
        years -= 1
        months += 12

    return years, months, days


# --- STREAMLIT UI ---

st.title(" NIC Details & Age Calculator")
st.write("Enter your full name and National Identity Card (NIC) number below.Created by Shenura Fernando.ALL rights reserved!")

# Form inputs
with st.form("user_form"):
    user_name = st.text_input("Enter Full Name:")
    nic_no = st.text_input("Enter NIC No. (e.g., 951234567V or 199512345678):")
    
    submitted = st.form_submit_button("Process Details")

if submitted:
    if not user_name.strip() or not nic_no.strip():
        st.warning("Please fill in both the Name and NIC fields.")
    else:
        # Process NIC
        nic_data, error = process_nic(nic_no)
        
        if error:
            st.error(error)
        else:
            # 1. Save details to file (id details.txt)
            with open('id details.txt', 'a') as f1:
                f1.write(f"{user_name}----{nic_no}.\n")

            st.success("processed successfully!")

            # 2. Calculate Exact Age
            years, months, days = calculate_age(nic_data["dob_date"])

            # 3. Display Results in Cards / Metrics
            st.markdown("### Processed Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gender", nic_data["gender"])
                st.metric("Birth Year", nic_data["birth_year"])
            
            with col2:
                st.metric("Date of Birth", f"{nic_data['day']} {nic_data['month']}")
                st.metric("Current Age", f"{years} Years, {months} Mos, {days} Days")
