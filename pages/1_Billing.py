import streamlit as st
import pandas as pd
from datetime import datetime, date
import time
import uuid

from student_db import Student_DB
from misc_functions import Misc_Functions

st.set_page_config(layout="wide")

st.write("## Charge Students")

db = Student_DB()

filter_options = ["Outstanding Fees", "All Students", "Find Student"]
filter = st.selectbox("Filter", options=filter_options, key="filter", index=1)

if filter == "Outstanding Fees":
    results = db.get_student_data({"balance": {"$lt": 1}})


if filter == "All Students":
    results = db.get_student_data({})

if filter == "Find Student":
    student_name = st.text_input("Student Name", key="manage_meeting_filter")
    results = db.get_student_data(
        {"name": {"$regex": f"^{student_name}", "$options": "i"}})

misc_function = Misc_Functions()
results = sorted(
    results, key=misc_function.sorting_key_group_alphabetical_dict)

st.write(f"### Total Students: {len(results)}")

if st.button("⟳", key="button_refresh1"):
    st.rerun()


markdown_header = misc_function.adjust_header_size()

c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 2, 1, 1, 2])
c2.write(f"{markdown_header} Name")
c3.write(f"{markdown_header} Phone Number")
c4.write(f"{markdown_header} Session Fee")
c5.write(f"{markdown_header} Outstanding Fees")
c6.write(f"{markdown_header} Balance")
st.divider()

student_name_list = []
student_phone_list = []
student_balance_list = []
student_session_fee = []
student_outstanding_fees = []
for i in results:
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 2, 1, 1, 2])

    if c1.checkbox("Checkbox", key=f'checkbox_{i["_id"]}', label_visibility="hidden"):
        student_name_list.append(i["name"])
        student_phone_list.append(i["phone_number"])
        student_balance_list.append("RM{:,.2f}".format(i["balance"]))
        student_session_fee.append("RM{:,.2f}".format(i["session_fee"]))

        if i["balance"] <= 0:
            student_outstanding_fees.append("✔️ Paid")
        else:
            student_outstanding_fees.append("❌ Unpaid")

    c2.write(f'{markdown_header} {i["name"]}')
    c3.write(f'{markdown_header} {i["phone_number"]}')

    c4.write("{} RM{:,.2f}".format(markdown_header, i["session_fee"]))
    if i["balance"] <= 0:

        c5.write(f"{markdown_header} ✔️ Paid")
        c6.write("{} :green[RM{:,.2f}]".format(markdown_header, i["balance"]))
    else:

        c5.write(f"{markdown_header} ❌ Unpaid")
        c6.write("{} :red[RM{:,.2f}]".format(markdown_header, i["balance"]))


st.divider()

df = pd.DataFrame({"Name": student_name_list,
                   "Phone Number": student_phone_list,
                   "Balance": student_balance_list,
                   "Session Fee": student_session_fee,
                   "Outstanding Fees": student_outstanding_fees
                   })
df.index += 1
st.write("### Students Selected:")
st.table(df)


if "charge_student" not in st.session_state:
    st.session_state.charge_student = False


charge_student = st.button("Charge Student(s)")

if charge_student:
    st.session_state.charge_student = True

if st.session_state.charge_student:
    misc_function = Misc_Functions()
    confirmed = misc_function.confirmation_check("charge_student")

    if confirmed:
        with st.spinner("Processing..."):
            if student_name_list:
                for student_name in student_name_list:
                    session_fee = db.get_student_session_fee(student_name)
                    db.push_student_transaction(student_name, session_fee, "debit", False, {
                        "transaction_id": str(uuid.uuid4()),
                        "transaction_type": "debit",
                        "amount": session_fee,
                        "balance_record": db.get_student_balance(student_name) + session_fee,
                        "description": "Fee",
                        "datetime": datetime.now()
                    })

            else:
                st.toast(
                    "###### 🟥 :red[Error:] No students found in the student list")
                st.error("No students found in the student list")
                time.sleep(2.5)
                st.rerun()

            st.toast(
                f"###### 🟩 :green[Success:] {len(student_name_list)} Student(s) have been charged")
            st.success(
                f"{len(student_name_list)} Student(s) have been charged")
            st.session_state.charge_student = False
    elif confirmed == False:
        st.session_state.charge_student = False

st.write("### Reminder:")
st.write('1. If there are no students to select from, please check the "Filter" select box')
st.write("2. Please refresh the page after clicking the 'Charge Student(s)' button to clear selected students if additional students are to be added. This is to ensure previous students are not given an additional charge")
