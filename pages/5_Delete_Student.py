import streamlit as st
import time
import pandas as pd
from datetime import datetime

from student_db import Student_DB
from misc_functions import Misc_Functions

st.set_page_config(layout="wide")

db = Student_DB()
student_list = db.get_student_list()


def sorting_key_group_alphabetical(item):
    if " - " in item:
        group, test = item.split(' - ')
        return (group, test)
    else:
        return ('', item)


student_list = sorted(student_list, key=sorting_key_group_alphabetical)

student_names = st.multiselect("Students", options=student_list)
df = pd.DataFrame({"Name": student_names
                   })
df.index += 1
st.write("### Students Selected:")
st.table(df)

if "delete_students" not in st.session_state:
    st.session_state.delete_students = False

delete_students = st.button("Delete Students")

if delete_students:
    st.session_state.delete_students = True

if st.session_state.delete_students:
    misc_functions = Misc_Functions()
    confirmed = misc_functions.confirmation_check(
        "delete_students")
    if confirmed:
        with st.spinner("Processing..."):
            for student_name in student_names:
                db.delete_student(
                    student_name)

            activity_data = {
                "name": ", ".join(student_names),
                "activity_name": "Deleted Student",
                "activity_description": ", ".join(student_names),
                "datetime": datetime.now()
            }
            db.insert_db_activity(activity_data)

            st.toast(
                "###### 🟩 :green[Success:] students deleted successfully")
            st.success("Students deleted successfully")
            st.session_state.delete_students = False
            time.sleep(2.5)
            st.rerun()
    elif confirmed == False:
        st.session_state.delete_students = False
        st.rerun()
