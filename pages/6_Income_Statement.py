import streamlit as st
import pandas as pd
from datetime import datetime

from student_db import Student_DB
from misc_functions import Misc_Functions

st.set_page_config(layout="wide")

st.write("## Income Statement")

misc_function = Misc_Functions()
db = Student_DB()

date_option, date_range = misc_function.date_filter()

student_data = list(db.get_student_data({}))

try:
    start_date = datetime.combine(date_range[0], datetime.min.time())
    end_date = datetime.combine(date_range[1], datetime.max.time())
except IndexError as e:
    st.error("Please select start date and end date")
    st.stop()


debit_list = []
credit_list = []

for idx, i in enumerate(student_data):
    for idx, x in enumerate(i["transaction"]):
        if start_date <= x["datetime"] <= end_date:
            if x["transaction_type"] == "debit":
                debit_list.append(x["amount"])
            else:
                credit_list.append(x["amount"])


total_debit = sum(debit_list)
total_credit = -sum(credit_list)
balance = total_debit + total_credit

if date_option == "Month":
    df = pd.DataFrame({
        "Date": f"{date_range[0].strftime('%B %Y')}",
        "Debit": "RM{:,.2f}".format(total_debit),
        "Credit": "RM{:,.2f}".format(total_credit),
        "Balance": "RM{:,.2f}".format(balance),
    }, index=[1])
else:
    df = pd.DataFrame({
        "Date": f"{start_date.strftime('%d-%m-%Y')} - {end_date.strftime('%d-%m-%Y')}",
        "Debit": "RM{:,.2f}".format(total_debit),
        "Credit": "RM{:,.2f}".format(total_credit),
        "Balance": "RM{:,.2f}".format(balance),
    }, index=[1])


st.table(df)
