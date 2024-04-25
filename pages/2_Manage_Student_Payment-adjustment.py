import streamlit as st
import uuid
import time
import csv
import io
from datetime import datetime

from student_db import Student_DB
from misc_functions import Misc_Functions

st.set_page_config(layout="wide")

st.write("## Manage Student Payments/Adjustments")

db = Student_DB()
student_list = db.get_student_list()


def sorting_key_group_alphabetical_list(item):
    if " - " in item:
        group, test = item.split(' - ')
        return (group, test)
    else:
        return ('', item)


def write_csv(student_name, date_option, date_range):
    results = db.get_student_data_one({"name": student_name})

    try:
        start_date = datetime.combine(date_range[0], datetime.min.time())
        end_date = datetime.combine(date_range[1], datetime.max.time())
    except IndexError as e:
        st.error("Please select start date and end date")
        time.sleep(3)
        st.rerun()

    document_idx = None
    previous_balance = None
    results_transaction = []
    for idx, i in enumerate(results["transaction"]):
        if start_date <= i["datetime"] <= end_date:
            if previous_balance == None:
                previous_balance = results["transaction"][idx -
                                                          1]["balance_record"]
            if document_idx == None:
                document_idx = idx
            results_transaction.append(i)

    if results_transaction:
        if document_idx < 1:
            description = []
            debit_list = []
            credit_list = []
            date_list = []
            time_list = []
        else:
            description = ["Prev. Bal."]
            debit_list = [""]
            credit_list = ["RM{:,.2f}".format(previous_balance)]
            date_list = [""]
            time_list = [""]

        for i in results_transaction:
            if i["transaction_type"] == "debit":
                debit_list.append("RM{:,.2f}".format(i["amount"]))
                credit_list.append(" ")
            else:
                credit_list.append("RM{:,.2f}".format(i["amount"]))
                debit_list.append(" ")

            description.append(i["description"])
            date_list.append(misc_function.convert_timezone(
                i["datetime"]).date().strftime("%d-%m-%Y"))
            time_list.append(misc_function.convert_timezone(
                i["datetime"]).time().strftime("%H:%M:%S"))
            previous_balance = i["balance_record"]

        student_report = {
            "Date": date_list,
            "Time": time_list,
            "Description": description,
            "Debit": debit_list,
            "Credit": credit_list,
        }

        rows = zip(date_list, time_list, description, debit_list, credit_list)
        if date_option == "Month":
            csv_file_name = f'{results["name"]}_Account_Statement_{date_range[0].strftime("%B_%Y")}.csv'
        else:
            csv_file_name = f'{results["name"]}_Account_Statement_{date_range[0]}_{date_range[1]}.csv'

        csv_buffer = io.StringIO()

        csv_writer_cell = csv.DictWriter(
            csv_buffer, fieldnames=student_report.keys())
        csv_writer = csv.writer(csv_buffer)
        csv_writer_cell.writerow(
            {"Time": "TUITION GURU LINA", "Credit": f"Date: {datetime.today().date()}"})
        csv_writer.writerow([""])
        csv_writer_cell.writerow({"Time": "Statement of Account"})
        if date_option == "Month":
            csv_writer_cell.writerow(
                {"Time": f"'{date_range[0].strftime('%B %Y')}"})
        else:
            csv_writer_cell.writerow(
                {"Time": f'From {date_range[0].strftime("%d-%m-%Y")} To {date_range[1].strftime("%d-%m-%Y")}'})
        csv_writer.writerow([""])
        csv_writer.writerow([f'Student Name: {results["name"]}'])
        csv_writer.writerow([f'Contact: {results["phone_number"]}'])
        csv_writer.writerow([""])
        csv_writer.writerow(student_report.keys())
        csv_writer.writerow(
            ["-----------------------------------------------------------------------------------------------------------"])
        for i in rows:
            csv_writer.writerow(i)
        csv_writer.writerow(
            ["-----------------------------------------------------------------------------------------------------------"])
        csv_writer_cell.writerow(
            {"Description": "Balance:", "Credit": "RM{:,.2f}".format(previous_balance)})

        with st.expander("Account Statement:", expanded=True):
            st.table(student_report)

    else:
        st.error("No records found for the given start and end date")
        time.sleep(3)
        st.rerun()

    return csv_buffer, csv_file_name


student_list = sorted(student_list, key=sorting_key_group_alphabetical_list)

filter_options = ["Outstanding Fees", "All Students", "Find Student"]
filter = st.selectbox("Filter", options=filter_options, index=1)

if filter == "Outstanding Fees":
    results = db.get_student_data({"balance": {"$lt": 1}})

if filter == "All Students":
    results = db.get_student_data({})

if filter == "Find Student":
    student_name = st.text_input("Student Name", key="manage_fees_filter")
    results = db.get_student_data(
        {"name": {"$regex": f"^{student_name}", "$options": "i"}})

misc_function = Misc_Functions()
results = sorted(
    results, key=misc_function.sorting_key_group_alphabetical_dict)

with st.expander("Manage Student Payments/Adjustments:", expanded=True):

    student_name = st.selectbox("Select Student", options=student_list)
    pay_adjust_list = ["Payment", "Adjustment"]
    transaction_type_list = ["Debit", "Credit"]
    pay_adjust = st.radio("pay_adjustment", pay_adjust_list,
                          label_visibility="hidden")

    if pay_adjust == pay_adjust_list[0]:
        amount = st.number_input("Amount (RM)", min_value=0.00)
        description = "Paid - Thank you"
    else:
        c1, c2, c3 = st.columns([1, 1, 2])

        transaction_type = c1.selectbox(
            "Transaction Type", options=transaction_type_list)
        amount = c2.number_input("Amount (RM)", min_value=0.00)
        description = c3.text_input("Description")

    deduct_fees_button = st.button("Confirm", key=123)

    if "deduct_fees_button" not in st.session_state:
        st.session_state.deduct_fees_button = False

    if deduct_fees_button:
        st.session_state.deduct_fees_button = True

    if st.session_state.deduct_fees_button:
        if amount < 1:
            st.toast("###### 🟥 :red[Error:] Payment amount cannot be RM0.00")
            st.error("Payment amount cannot be RM0.00")
            st.session_state.deduct_fees_button = False
            time.sleep(2.5)
            st.rerun()
        elif not description:
            st.toast("###### 🟥 :red[Error:] Please enter a description")
            st.error("Please enter a description")

        else:
            misc_function = Misc_Functions()
            confirmed = misc_function.confirmation_check("deduct_fees_button")
            if confirmed:
                with st.spinner("Processing..."):
                    if pay_adjust == pay_adjust_list[0]:
                        db.push_student_transaction(student_name, amount, "credit", False, {
                            "transaction_id": str(uuid.uuid4()),
                            "transaction_type": "credit",
                            "amount": amount,
                            "balance_record": db.get_student_balance(student_name) - amount,
                            "description": description,
                            "datetime": datetime.now()
                        })

                        st.toast("###### 🟩 :green[Success:] Payment Updated")
                        st.success("Payment Updated")
                        st.session_state.deduct_fees_button = False
                        time.sleep(2.5)
                        st.rerun()

                    if transaction_type == transaction_type_list[0]:
                        db.push_student_transaction(student_name, amount, "debit", True, {
                            "transaction_id": str(uuid.uuid4()),
                            "transaction_type": "debit",
                            "amount": amount,
                            "balance_record": db.get_student_balance(student_name) + amount,
                            "description": description,
                            "datetime": datetime.now()
                        })

                        st.toast("###### 🟩 :green[Success:] Payment Updated")
                        st.success("Payment Updated")
                        st.session_state.deduct_fees_button = False
                        time.sleep(2.5)
                        st.rerun()
                    else:
                        db.push_student_transaction(student_name, amount, "credit", True, {
                            "transaction_id": str(uuid.uuid4()),
                            "transaction_type": "credit",
                            "amount": amount,
                            "balance_record": db.get_student_balance(student_name) - amount,
                            "description": description,
                            "datetime": datetime.now()
                        })

                        st.toast("###### 🟩 :green[Success:] Payment Updated")
                        st.success("Payment Updated")
                        st.session_state.deduct_fees_button = False
                        time.sleep(2.5)
                        st.rerun()
            elif confirmed == False:
                st.session_state.deduct_fees_button = False
                st.rerun()

st.divider()

date_option, date_range = misc_function.date_filter()

st.write(f"### Total Students: {len(results)}")

if st.button("⟳", key="button_refresh"):
    st.rerun()

markdown_header = misc_function.adjust_header_size()

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2, 3, 2, 2, 2, 2, 3])
c1.write(f"{markdown_header} Name")
c2.write(f"{markdown_header} Phone Number")
c3.write(f"{markdown_header} Email")
c4.write(f"{markdown_header} Session fee")
c5.write(f"{markdown_header} Outstanding Fees")
c6.write(f"{markdown_header} Balance")
c7.write(f"{markdown_header} Date Registered")
st.divider()

for i in results:
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2, 3, 2, 2, 2, 2, 3])
    c1.write(f'{markdown_header} {i["name"]}')
    c2.write(f'{markdown_header} {i["phone_number"]}')
    st.markdown("""
    <style>
        .st-emotion-cache-1kn7chm a {
            color: rgb(255 255 255);
        }
    </style>
    """, unsafe_allow_html=True)
    c3.write(f'{markdown_header} {i["email"]}')
    c4.write("{} RM{:,.2f}".format(markdown_header, i["session_fee"]))
    if i["balance"] <= 0:
        c5.write(f"{markdown_header} ✔️ Paid")
        c6.write("{} :green[RM{:,.2f}]".format(markdown_header, i["balance"]))
    else:
        c5.write(f"{markdown_header} ❌ Unpaid")
        c6.write("{} :red[RM{:,.2f}]".format(markdown_header, i["balance"]))

    c7.write(f'{markdown_header} {i["date_registered"].date()}')
    if c8.button("View Account Statement", key=f'csv_{i["_id"]}'):
        csv_file, csv_file_name = write_csv(i["name"], date_option, date_range)
        csv_file.seek(0)
        download_csv = c8.download_button(
            "Download as CSV", data=csv_file.read(), file_name=csv_file_name, mime='text/csv')

    st.divider()
