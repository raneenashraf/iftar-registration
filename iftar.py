import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import base64

FILE_NAME = "iftar_data.xlsx"
TICKET_PRICE = 250

st.set_page_config(page_title="Iftar Registration Dashboard", layout="wide")

# -----------------------
# BACKGROUND IMAGE
# -----------------------
def set_bg(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()

    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)),
                          url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}

    h1, h2, h3, label, p {{
        color: white !important;
        font-weight: bold;
    }}

    /* metric value */
    [data-testid="stMetricValue"] {{
        color: white !important;
        font-weight: bold;
    }}

    /* metric label */
    [data-testid="stMetricLabel"] {{
        color: white !important;
    }}
             /* شكل الزرار العادي */
    .stButton > button {{
    background-color: #1f4e79 !important;   /* لون أزرق غامق شيك */
    color: white !important;                /* النص أبيض دايمًا */
    border: 1px solid white !important;
    font-weight: bold;
}}

/* لما تقفي عليه */
   .stButton > button:hover
   .stDownloadButton > button,
div[data-testid="stFormSubmitButton"] > button {{

    background-color: #1f4e79 !important;   /* لون الخلفية */
    color: white !important;                /* النص أبيض */
    border: 2px solid white !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
}}

/* hover */
.stButton > button:hover,
.stDownloadButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover 

    background-color: #2e6da4 !important;
    color: white !important;
    border: 2px solid white !important;
{{
    background-color: #2e6da4 !important;
    color: white !important;
    border: 1px solid white !important;
}}
    

    </style>
    """
    ,
    unsafe_allow_html=True
    
)


set_bg("background1.jpg")

st.title("🎟 Iftar Registration")

# -----------------------
# LOAD DATA
# -----------------------
if os.path.exists(FILE_NAME):
    df_existing = pd.read_excel(FILE_NAME)
    last_ticket = df_existing["Ticket Number"].max()
else:
    df_existing = pd.DataFrame()
    last_ticket = 0

# -----------------------
# FORM
# -----------------------
with st.form("registration_form"):

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Student Name")
        student_id = st.text_input("Student ID")
        department = st.selectbox(
            "Department",
            ["Data Science", "AI", "Cyber", "Healthcare", "Media"]
        )

    with col2:
        level = st.selectbox("Level", ["1", "2", "3", "4"])
        meal = st.selectbox("Meal", ["Meat", "Chicken", "Syamii"])
        companions = st.number_input("Number of Companions", min_value=0, step=1)

        companion_meals = []
        for i in range(companions):
            meal_choice = st.selectbox(
                f"Meal for Companion {i+1}",
                ["Meat", "Chicken", "Syamii"],
                key=f"companion_{i}"
            )
            companion_meals.append(meal_choice)

    submitted = st.form_submit_button("Submit")

# -----------------------
# AFTER SUBMIT
# -----------------------
if submitted:

    new_ticket = last_ticket + 1
    total_people = 1 + companions
    total_price = total_people * TICKET_PRICE

    all_meals = [meal] + companion_meals
    meal_summary = ", ".join(all_meals)

    new_data = pd.DataFrame({
        "Ticket Number": [new_ticket],
        "Name": [name],
        "Student ID": [student_id],
        "Department": [department],
        "Level": [level],
        "Meal": [meal],
        "Meals Details": [meal_summary],
        "Companions": [companions],
        "Total People": [total_people],
        "Total Price": [total_price],
        "Timestamp": [datetime.now()]
    })

    updated = pd.concat([df_existing, new_data], ignore_index=True)
    updated.to_excel(FILE_NAME, index=False)

    st.success("✅ Registration Successful!")
    st.markdown(f"## 🎟 Ticket Number: {new_ticket}")
    st.markdown(f"### 💰 Total Amount: {total_price} EGP")

# -----------------------
# ANALYSIS SECTION
# -----------------------
if os.path.exists(FILE_NAME):

    df = pd.read_excel(FILE_NAME)

    st.divider()

    with st.expander("📊 Show Dashboard Analysis", expanded=False):

        # -----------------------
        # Metrics
        # -----------------------
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Registrations", len(df))
        col2.metric("Total Revenue", f"{df['Total Price'].sum()} EGP")
        col3.metric("Total Attendees", df["Total People"].sum())

        # -----------------------
        # MEAL DISTRIBUTION
        # -----------------------
        st.subheader("🍽 Meal Distribution")

        all_meals_list = []

        if "Meals Details" in df.columns:
            for meals in df["Meals Details"]:
                if pd.notna(meals):
                    split_meals = [m.strip() for m in str(meals).split(",")]
                    all_meals_list.extend(split_meals)
        else:
            all_meals_list = df["Meal"].dropna().tolist()

        if len(all_meals_list) > 0:
            meal_counts = pd.Series(all_meals_list).value_counts()

            fig1, ax1 = plt.subplots()
            ax1.pie(
                meal_counts.values,
                labels=meal_counts.index,
                autopct='%1.1f%%',
                textprops={'color': "white"}
            )
            fig1.patch.set_facecolor('none')
            ax1.set_facecolor('none')
            st.pyplot(fig1)
        else:
            st.info("No meal data available yet.")

        # -----------------------
        # DEPARTMENT DISTRIBUTION
        # -----------------------
        st.subheader("🏫 Department Distribution")

        dept_counts = df["Department"].value_counts()

        fig2, ax2 = plt.subplots()
        ax2.bar(dept_counts.index, dept_counts.values)

        ax2.tick_params(axis='x', colors='white', rotation=45)
        ax2.tick_params(axis='y', colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')

        fig2.patch.set_facecolor('none')
        ax2.set_facecolor('none')

        st.pyplot(fig2)

        # -----------------------
        # REVENUE BY DEPARTMENT
        # -----------------------
        st.subheader("💰 Revenue by Department")

        revenue_dept = df.groupby("Department")["Total Price"].sum()

        fig3, ax3 = plt.subplots()
        ax3.bar(revenue_dept.index, revenue_dept.values)

        ax3.tick_params(axis='x', colors='white', rotation=45)
        ax3.tick_params(axis='y', colors='white')
        ax3.spines['bottom'].set_color('white')
        ax3.spines['left'].set_color('white')

        fig3.patch.set_facecolor('none')
        ax3.set_facecolor('none')

        st.pyplot(fig3)

        st.divider()
        st.dataframe(df)

    # -----------------------
    # CLEAR BUTTONS
    # -----------------------
    colA, colB = st.columns(2)

    with colA:
        if st.button("🗑 Clear Last Record"):
            df = df.iloc[:-1]
            df.to_excel(FILE_NAME, index=False)
            st.success("Last record deleted")
            st.rerun()

    with colB:
        if st.button("❌ Clear All Data"):
            os.remove(FILE_NAME)
            st.success("All data deleted")
            st.rerun()

    with open(FILE_NAME, "rb") as file:
        st.download_button(
            label="⬇ Download Excel File",
            data=file,
            file_name="iftar_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
