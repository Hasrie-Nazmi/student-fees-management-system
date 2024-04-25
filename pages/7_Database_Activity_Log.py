import streamlit as st
from datetime import datetime
import time

from student_db import Student_DB
from misc_functions import Misc_Functions

st.set_page_config(layout="wide")

db = Student_DB()
misc_function = Misc_Functions()

filter_options = ["No Filter", "Filter"]
filter_select = st.selectbox("Filter Type", filter_options)

if filter_select == filter_options[0]:
    db_activity_list = db.get_db_activity()
else:
    c1, c2 = st.columns([1, 1])
    student_filter_options = ["All Students", "Find Student"]
    db_activity_type = ["Registered Student", "Charged Student", "Added Student Payment",
                        "Added Adjustment - Debit", "Added Adjustment - Credit", "Modified Student Details", "Deleted Student Transaction"]

    misc_function = Misc_Functions()
    date_option, date_range = misc_function.date_filter()

    try:
        start_date = datetime.combine(date_range[0], datetime.min.time())
        end_date = datetime.combine(date_range[1], datetime.max.time())
    except IndexError as e:
        st.error("Please select start date and end date")
        time.sleep(3)
        st.rerun()

    student_filter_select = c1.selectbox(
        "Student Filter", student_filter_options)
    db_activity_select = c2.multiselect(
        "Select Activity Name(s)", db_activity_type)

    activity_type_filter = {"activity_name": {"$in": db_activity_select}}
    datetime_filter = {"datetime": {
        "$gte": start_date, "$lte": end_date}}

    if student_filter_select == student_filter_options[0]:
        db_activity_list = db.get_db_activity(
            {"$and": [activity_type_filter, datetime_filter]})
    else:
        student_name = st.text_input("Student Name")
        student_name_filter = {"name": student_name}
        db_activity_list = db.get_db_activity(
            {"$and": [student_name_filter, activity_type_filter, datetime_filter]})


id_list = []
name_list = []
activity_name_list = []
activity_desc = []
datetime_list = []

for data in db_activity_list:
    id_list.append(str(data["_id"]))
    name_list.append(data["name"])
    activity_name_list.append(data["activity_name"])
    datetime_list.append(misc_function.convert_timezone(
        data["datetime"]).strftime('%d-%m-%Y %H:%M:%S'))

    activity_desc_str = ""
    if type(data["activity_description"]) is list:
        for idx, i in enumerate(data["activity_description"]):
            activity_desc_str = activity_desc_str + \
                f' DOCUMENT {idx+1}: {str(i)}'
        activity_desc.append(activity_desc_str)
    else:
        activity_desc.append(str(data["activity_description"]))

activity_data = {
    "ID": id_list,
    "Student Name": name_list,
    "Activity Name": activity_name_list,
    "Activity Description": activity_desc,
    "Datetime": datetime_list
}

st.table(activity_data)
