import streamlit as st
import re
import time
from datetime import datetime

from student_db import Student_DB
from misc_functions import Misc_Functions

st.set_page_config(layout="wide")

st.write("## Edit Student Data")

db = Student_DB()
student_list = db.get_student_list()


def sorting_key_group_alphabetical(item):
    if " - " in item:
        group, test = item.split(' - ')
        return (group, test)
    else:
        return ('', item)


student_list = sorted(student_list, key=sorting_key_group_alphabetical)

c1, c2, c3 = st.columns([2, 1, 1])
student_name = c1.selectbox("Select student to edit", student_list)
edit_options = ["Student details", "Transactions"]
edit_select = c2.selectbox("Student data to edit", options=edit_options)

st.divider()

if edit_select == edit_options[0]:
    results = db.get_student_data_one({"name": student_name})
    if results:
        pass
    else:
        st.toast(
            '###### 🟥 :red[Error:] No student data in database, please register in the "Register Student" tab')
        st.error(
            'No student data in database, please register in the "Register Student" tab')
        st.stop()

    c1, c2, c3 = st.columns([2, 1, 1])
    name = c1.text_input("Name", value=results["name"])
    email = st.text_input("Email", results["email"])
    phone_number = c2.text_input(
        "Phone Number", value=results["phone_number"], max_chars=13)
    session_fee = c3.number_input(
        "Fee Per Session (RM)", value=float(results["session_fee"]), min_value=0.00)

    if "confirm_edit" not in st.session_state:
        st.session_state.confirm_edit = False

    confirm_edit = st.button("Confirm Edit")
    if confirm_edit:
        st.session_state.confirm_edit = True

    if st.session_state.confirm_edit:
        misc_functions = Misc_Functions()
        confirmed = misc_functions.confirmation_check("confirm_edit")
        if confirmed:
            with st.spinner("Processing..."):
                if name == results["name"] or not db.student_registered_name(name):
                    if not name:
                        st.toast("###### 🟥 :red[Error:] Please enter name")
                        st.error("Please enter name")
                    elif not email:
                        st.toast("###### 🟥 :red[Error:] Please enter email")
                        st.error("Please enter email")
                    elif not phone_number:
                        st.toast(
                            "###### 🟥 :red[Error:] Please enter phone number")
                        st.error("Please enter phone number")
                    elif len(phone_number) < 12:
                        st.toast(
                            "###### 🟥 :red[Error:] Incorrect phone number length, must be atleast 12 characters")
                        st.error(
                            "Incorrect phone number length, must be atleast 12 characters")
                    elif re.search('[a-zA-Z]', phone_number):
                        st.toast(
                            "###### 🟥 :red[Error:] Phone number must not contain letters")
                        st.error("Phone number must not contain letters")
                    elif session_fee < 1:
                        st.toast(
                            "###### 🟥 :red[Error:] Session fee amount cannot be RM0.00")
                        st.error("Session fee amount cannot be RM0.00")
                    else:
                        db.modify_student_details(
                            {"name": results["name"],
                             "phone_number": results["phone_number"],
                             "email": results["email"],
                             "session_fee": results["session_fee"]},
                            {"name": name,
                             "email": email,
                             "phone_number": phone_number,
                             "session_fee": session_fee})

                        st.toast(
                            "###### 🟩 :green[Success:] Student details updated")
                        st.success("Student details updated")
                        st.session_state.confirm_edit = False
                        time.sleep(2.5)
                        st.rerun()
                else:
                    st.toast(
                        "###### 🟥 :red[Error:] A student with this name is already registered")
                    st.error("A student with this name is already registered")

        elif confirmed == False:
            st.session_state.confirm_edit = False
            st.rerun()

else:
    transaction_options = ["Edit transaction", "Delete Transactions"]
    transaction_select = c3.selectbox(
        "Transaction edit option", transaction_options)

    results = db.get_student_data_one({"name": student_name})
    if results:
        pass
    else:
        st.toast(
            '###### 🟥 :red[Error:] No student data in database, please register in the "Register Student" tab')
        st.error(
            'No student data in database, please register in the "Register Student" tab')
        st.stop()

    transaction_list = list(results["transaction"])
    if transaction_list:
        pass
    else:
        st.toast('###### 🟥 :red[Error:]No transaction data found in database')
        st.error(":red[Error:]No transaction data found in database")
        st.stop()

    if transaction_select == transaction_options[0]:
        misc_function = Misc_Functions()
        transaction = st.selectbox(
            "Transactions", options=transaction_list)

        transaction_id_text = st.text_input(
            "Transaction ID", value=transaction["transaction_id"], disabled=True)
        c1, c2, c3 = st.columns([1, 1, 1])

        transaction_type_options = ["debit", "credit"]
        if transaction["transaction_type"] == transaction_type_options[0]:
            transaction_type_index = 0
        else:
            transaction_type_index = 1

        transaction_type = c1.selectbox(
            "Transaction Type", index=transaction_type_index, options=["debit", "credit"])
        amount = c2.number_input(
            "Amount", value=float(transaction["amount"]), min_value=0.00)
        c3.number_input("Balance Record", value=transaction["balance_record"],
                        disabled=True, help="This value will be updated automatically")
        transaction_description = c1.text_input(
            "Description", value=transaction["description"])
        transaction_date = c2.date_input(
            "Date", value=misc_function.convert_timezone(
                transaction["datetime"]).date())
        transaction_time = c3.time_input(
            "Time", value=misc_function.convert_timezone(
                transaction["datetime"]).time())
        transaction_datetime = datetime.combine(
            transaction_date, transaction_time)

        if "confirm_edit_transaction" not in st.session_state:
            st.session_state.confirm_edit_transaction = False

        confirm_edit_transaction = st.button("Confirm Edit")

        if confirm_edit_transaction:
            st.session_state.confirm_edit_transaction = True

        if st.session_state.confirm_edit_transaction:
            misc_functions = Misc_Functions()
            confirmed = misc_functions.confirmation_check(
                "confirm_edit_transaction")
            if confirmed:
                with st.spinner("Processing..."):
                    db.modify_student_transactions({
                        "transaction_id": transaction_id_text,
                        "transaction_type": transaction_type,
                        "amount": amount,
                        "description": transaction_description,
                        "datetime": transaction_datetime
                    }, student_name, transaction_list.index(transaction))

                    st.toast(
                        "###### 🟩 :green[Success:] Transaction modified successfully")
                    st.success("Transaction modified successfully")
                    st.session_state.confirm_edit_transaction = False
                    time.sleep(2.5)
                    st.rerun()
            elif confirmed == False:
                st.session_state.confirm_edit_transaction = False
                st.rerun()

    else:
        transactions = st.multiselect("Transactions", options=transaction_list)
        st.write("### Selected Transactions")
        st.table(transactions)

        if "delete_transactions" not in st.session_state:
            st.session_state.delete_transactions = False

        delete_transactions = st.button("Delete Transactions")

        if delete_transactions:
            st.session_state.delete_transactions = True

        if st.session_state.delete_transactions:
            misc_functions = Misc_Functions()
            confirmed = misc_functions.confirmation_check(
                "delete_transactions")
            if confirmed:
                with st.spinner("Processing..."):
                    for transaction in transactions:
                        db.delete_student_transactions(
                            student_name, transaction["transaction_id"], transaction_list.index(transaction))

                    activity_data = {
                        "name": student_name,
                        "activity_name": "Deleted Student Transaction",
                        "activity_description": transactions,
                        "datetime": datetime.now()
                    }
                    db.insert_db_activity(activity_data)

                    st.toast(
                        "###### 🟩 :green[Success:] Transactions deleted successfully")
                    st.success("Transactions deleted successfully")
                    st.session_state.delete_transactions = False
                    time.sleep(2.5)
                    st.rerun()
            elif confirmed == False:
                st.session_state.delete_transactions = False
                st.rerun()
