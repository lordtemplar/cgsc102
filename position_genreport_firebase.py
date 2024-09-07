import streamlit as st
from firebase_admin import db
from firebase_connection import initialize_firebase

# Initialize Firebase connections
app1, app2 = initialize_firebase()

def fetch_data_by_index_range(start_index, end_index):
    """
    Fetches data from both Firebase databases using a range of indices.

    Args:
        start_index (int): The starting index for fetching data.
        end_index (int): The ending index for fetching data.
    """
    # Fetch data from the first Firebase database (internal-student-db)
    all_students_data = {}
    for index in range(start_index, end_index + 1):
        student_ref = db.reference(f'/students/{index}', app=app1)
        student_data = student_ref.get()
        all_students_data[index] = student_data
    st.write("All Students Data:", all_students_data)

    # Fetch data from the second Firebase database (internal-position-db)
    all_positions_data = {}
    for index in range(start_index, end_index + 1):
        position_ref = db.reference(f'/positions/{index}', app=app2)
        position_data = position_ref.get()
        all_positions_data[index] = position_data
    st.write("All Positions Data:", all_positions_data)

# Fetch data from both databases using indices 0 to 173
fetch_data_by_index_range(0, 173)
