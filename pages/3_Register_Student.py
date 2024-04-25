import streamlit as st
import re
import uuid
from datetime import datetime
import time

from student_db import Student_DB

st.set_page_config(layout="wide")

st.write("## Register Student")

db = Student_DB()

with st.form("register_student", clear_on_submit=True):

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number", value="+60", max_chars=13)
    c1, c2 = st.columns([2, 1])
    payment = c1.number_input("Payment (RM)", min_value=0.00)
    session_fee = c2.number_input(
        "Fee Per Session (RM)", min_value=0.00)

    submitted = st.form_submit_button("Submit")
    if submitted:
        if not name:
            st.toast("###### 🟥 :red[Error:] Please enter name")
            st.error("Please enter name")
        elif not email:
            st.toast("###### 🟥 :red[Error:] Please enter email")
            st.error("Please enter email")
        elif not phone_number:
            st.toast("###### 🟥 :red[Error:] Please enter phone number")
            st.error("Please enter phone number")
        elif len(phone_number) < 12:
            st.toast(
                "###### 🟥 :red[Error:] Incorrect phone number length, must be atleast 12 characters")
            st.error("Incorrect phone number length, must be atleast 12 characters")
        elif re.search('[a-zA-Z]', phone_number):
            st.toast(
                "###### 🟥 :red[Error:] Phone number must not contain letters")
            st.error("Phone number must not contain letters")
        elif db.student_registered_name(name):
            st.toast(
                "###### 🟥 :red[Error:] A student with this name is already registered")
            st.error("A student with this name is already registered")
        elif session_fee < 1:
            st.toast(
                "###### 🟥 :red[Error:] Session fee amount cannot be RM0.00")
            st.error("Session fee amount cannot be RM0.00")

        else:
            with st.spinner("Processing..."):
                db.insert_student_data({
                    "name": name,
                    "phone_number": phone_number,
                    "email": email,
                    "balance": 0,
                    "session_fee": session_fee,
                    "date_registered": datetime.now(),
                    "transaction": [{
                        "transaction_id": str(uuid.uuid4()),
                        "transaction_type": "credit",
                        "amount": 0,
                        "balance_record": 0,
                        "description": "Prev. Bal.",
                        "datetime": datetime.now()
                    }],
                })
                db.push_student_transaction(
                    name,
                    payment,
                    "credit",
                    False,
                    {
                        "transaction_id": str(uuid.uuid4()),
                        "transaction_type": "credit",
                        "amount": payment,
                        "balance_record": payment,
                        "description": "Paid - Thank you",
                        "datetime": datetime.now()
                    })
                st.toast(
                    "###### 🟩 :green[Success:] Student registered successfully")
                st.success("Student registered successfully")
                time.sleep(2.5)
                st.rerun()
