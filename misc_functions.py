import streamlit as st
from datetime import datetime, date
import pytz


class Misc_Functions:

    # Function to sort student name dictionary alphabetically and by prefix e.g: G1
    def sorting_key_group_alphabetical_dict(self, item):
        if " - " in item['name']:
            prefix, name = item['name'].split(' - ', 1)
            return (prefix, name)
        else:
            return ('', item['name'])

    # Confirmation dialog function
    def confirmation_check(self, key):
        st.warning(f"Are you sure?")
        c1, c2 = st.columns([1, 2])
        confirm = c1.button("Confirm", key=f"confirm_{key}")
        cancel = c2.button("Cancel", key=f"cancel_{key}")
        confirmed = None

        if confirm:
            confirmed = True
        if cancel:
            confirmed = False
        return confirmed

    def date_filter(self):
        c1, c2 = st.columns([1, 2])
        date_option_list = ["Month", "Custom Range"]
        months_dict = {
            "January": (date(datetime.now().year, 1, 1), date(datetime.now().year, 1, 31)),
            "February": (date(datetime.now().year, 2, 1), date(datetime.now().year, 2, 28)),
            "March": (date(datetime.now().year, 3, 1), date(datetime.now().year, 3, 31)),
            "April": (date(datetime.now().year, 4, 1), date(datetime.now().year, 4, 30)),
            "May": (date(datetime.now().year, 5, 1), date(datetime.now().year, 5, 31)),
            "June": (date(datetime.now().year, 6, 1), date(datetime.now().year, 6, 30)),
            "July": (date(datetime.now().year, 7, 1), date(datetime.now().year, 7, 31)),
            "August": (date(datetime.now().year, 8, 1), date(datetime.now().year, 8, 31)),
            "September": (date(datetime.now().year, 9, 1), date(datetime.now().year, 9, 30)),
            "October": (date(datetime.now().year, 10, 1), date(datetime.now().year, 10, 31)),
            "November": (date(datetime.now().year, 11, 1), date(datetime.now().year, 11, 30)),
            "December": (date(datetime.now().year, 12, 1), date(datetime.now().year, 12, 31))}

        date_option = c1.selectbox(
            "Date Range Option", options=date_option_list)

        if date_option == date_option_list[0]:
            date_range = c2.selectbox("Months", months_dict.keys())
            date_range = months_dict[date_range]

        else:
            date_range = c2.date_input("Date Range for Report", value=[
                datetime.today(), datetime.today()], format="DD/MM/YYYY")

        return date_option, date_range

    def adjust_header_size(self):
        header_size_value = st.sidebar.slider("Student List Font Size",
                                              min_value=1, max_value=4, value=1)
        markdown_header = "###"
        for i in range(header_size_value, 4):
            markdown_header = markdown_header + "#"
        return markdown_header

    def convert_timezone(self, datetime):
        malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        malaysia_time_local = datetime.replace(
            tzinfo=pytz.utc).astimezone(malaysia_timezone)

        return malaysia_time_local
