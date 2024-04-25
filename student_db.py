from pymongo import MongoClient
import streamlit as st
from datetime import datetime


class Student_DB:
    def __init__(self):
        self.open_db_connection()

    def open_db_connection(self, collection_name="student_collection"):
        self.client = MongoClient(st.secrets["db_connection"])
        db = self.client["student_db"]
        self.collection = db[collection_name]

    def insert_document(self, document):
        result = self.collection.insert_one(document)
        return result.inserted_id

    def find_document(self, query):
        query_results = self.collection.find_one(query)
        return query_results

    def find_documents(self, query):
        query_results = self.collection.find(query)
        return query_results

    def push_transaction(self, student_name, transaction):
        result = self.collection.update_one(
            {"name": student_name}, {"$push": {"transaction": transaction}})
        return result

    def update_balance(self, student_name, amount, transaction_type):
        if transaction_type == "debit":
            result = self.collection.update_one(
                {"name": student_name}, {"$inc": {"balance": +amount}})
            return result

        if transaction_type == "credit":
            result = self.collection.update_one(
                {"name": student_name}, {"$inc": {"balance": -amount}})
            return result

    def update_balance_direct(self, student_name, balance):
        result = self.collection.update_one(
            {"name": student_name}, {"$set": {"balance": balance}})
        return result

    def update_transaction_balance_record(self, student_name, idx, balance_record):
        result = self.collection.update_one({"name": student_name}, {"$set": {f"transaction.{idx}.balance_record": balance_record
                                                                              }
                                                                     })
        return result

    def update_transaction(self, document, student_name, idx):
        result = self.collection.update_one({f"name": student_name}, {"$set": {f"transaction.{idx}": document
                                                                               }
                                                                      })
        return result

    def delete_transaction(self, student_name, transaction_id):
        result = self.collection.update_one(
            {"name": student_name},
            {"$pull": {"transaction": {"transaction_id": transaction_id}}}
        )
        return result

    def update_student_details(self, query, document):
        result = self.collection.update_one(query, {"$set": document})
        return result

    def close_db_connection(self):
        self.client.close()

    # Database function to modify student details

    def modify_student_details(self, query, document):
        self.open_db_connection()
        self.update_student_details(query, document)
        activity_data = {
            "name": document["name"],
            "activity_name": "Modified Student Details",
            "activity_description": (query, document),
            "datetime": datetime.now()
        }

        self.insert_db_activity(activity_data)
        self.close_db_connection()

    # Database function to modify student transactions
    def modify_student_transactions(self, document, student_name, idx):
        try:
            self.open_db_connection()
            self.update_transaction(document, student_name, idx)

            results = self.get_student_data_one({"name": student_name})
            self.recalculate_update_balance_records(results, student_name)
            activity_data = {
                "name": student_name,
                "activity_name": "Modified Student Transaction",
                "activity_description": document,
                "datetime": datetime.now()
            }

            self.insert_db_activity(activity_data)
            self.close_db_connection()
        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to delete student transactions
    def delete_student_transactions(self, student_name, transaction_id, idx):
        try:
            self.open_db_connection()
            self.delete_transaction(student_name, transaction_id)

            results = self.get_student_data_one({"name": student_name})
            self.recalculate_update_balance_records(results, student_name)
            self.close_db_connection()
        except TypeError as e:
            st.error(e)
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to recalculate all balance records after updating transactions
    def recalculate_update_balance_records(self, student_data, student_name):
        try:
            self.open_db_connection()
            recalculated_balance = 0
            for idx, transaction in enumerate(student_data["transaction"]):
                if transaction["transaction_type"] == "debit":
                    recalculated_balance = recalculated_balance + \
                        transaction["amount"]
                    self.update_transaction_balance_record(
                        student_data["name"], idx, recalculated_balance)

                else:
                    recalculated_balance = recalculated_balance - \
                        transaction["amount"]
                    self.update_transaction_balance_record(
                        student_data["name"], idx, recalculated_balance)

            self.update_balance_direct(student_name, recalculated_balance)
            self.close_db_connection()

        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    def recalculate_all_student_balance(self):
        self.open_db_connection()
        student_data_list = list(self.get_student_data({}))
        for student_data in student_data_list:
            # st.write(student_data["name"],student_data)
            self.recalculate_update_balance_records(
                student_data, student_data["name"])

    # Database function to get multiple student data

    def get_student_data(self, query):
        try:
            self.open_db_connection()
            results = self.find_documents(query)

            student_data = []
            for data in results:
                student_data.append(data)

            self.close_db_connection()
            return student_data
        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to get one student data
    def get_student_data_one(self, query):
        try:
            self.open_db_connection()
            results = self.find_document(query)

            self.close_db_connection()
            return results
        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to insert student data
    def insert_student_data(self, insert_document):
        self.open_db_connection()
        self.insert_document(insert_document)
        activity_data = {
            "name": insert_document["name"],
            "activity_name": "Registered Student",
            "activity_description": insert_document,
            "datetime": datetime.now()
        }
        self.insert_db_activity(activity_data)
        self.close_db_connection()

    # Database function to append new transaction
    def push_student_transaction(self, name, amount, transaction_type, adjustment, push_transaction):
        self.open_db_connection()
        self.update_balance(name, amount, transaction_type)
        self.push_transaction(name, push_transaction)

        if adjustment:
            if transaction_type == "debit":
                activity_name = "Added Adjustment - Debit"
            else:
                activity_name = "Added Adjustment - Credit"

        else:
            if transaction_type == "debit":
                activity_name = "Charged Student"
            else:
                activity_name = "Added Student Payment"

        activity_data = {
            "name": name,
            "activity_name": activity_name,
            "activity_description": push_transaction,
            "datetime": datetime.now()

        }
        self.insert_db_activity(activity_data)
        self.close_db_connection()

    # Database function to get student fee
    def get_student_session_fee(self, student_name):
        try:
            self.open_db_connection()
            query_results = self.find_document({"name": student_name})
            self.close_db_connection()
            return query_results["session_fee"]

        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to get a list of student names
    def get_student_list(self):
        try:
            self.open_db_connection()
            query_results = self.find_documents({})

            student_list = []
            for i in query_results:
                student_list.append(i["name"])
            self.close_db_connection()

            return student_list

        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to get a student balance
    def get_student_balance(self, student_name):
        try:
            self.open_db_connection()
            query_results = self.find_document({"name": student_name})
            self.close_db_connection()
            return query_results["balance"]

        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    # Database function to check if student is already registered
    def student_registered_name(self, student_name):
        try:
            self.open_db_connection()
            query_results = self.find_document({"name": student_name})
            self.close_db_connection()

            if query_results:
                return True
            else:
                return False
        except TypeError as e:
            st.error(
                'No student data in database, please register in the "Register Student" tab')

    def delete_student(self, student_name):
        self.open_db_connection()
        self.collection.delete_one({"name": student_name})
        self.close_db_connection()

    def insert_db_activity(self, document):
        self.open_db_connection(collection_name="db_activity_collection")
        self.insert_document(document)
        self.close_db_connection()

    def get_db_activity(self, query={}):
        self.open_db_connection(collection_name="db_activity_collection")
        results = self.find_documents(query)

        db_activity_list = []
        for data in results:
            db_activity_list.append(data)

        self.close_db_connection()
        return db_activity_list[::-1]
