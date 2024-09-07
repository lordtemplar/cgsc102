import logging
import streamlit as st
from firebase_admin import db
from firebase_connection import initialize_firebase

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    try:
        all_students_data = {}
        for index in range(start_index, end_index + 1):
            student_ref = db.reference(f'/students/{index}', app=app1)
            student_data = student_ref.get()
            all_students_data[index] = student_data
            logging.debug(f"Fetched student data for index {index}: {student_data}")
        st.write("All Students Data:", all_students_data)
    except Exception as e:
        logging.error(f"Error fetching student data: {e}")
        st.error(f"Error fetching student data: {e}")

    # Fetch data from the second Firebase database (internal-position-db)
    try:
        all_positions_data = {}
        for index in range(start_index, end_index + 1):
            position_ref = db.reference(f'/positions/{index}', app=app2)
            position_data = position_ref.get()
            all_positions_data[index] = position_data
            logging.debug(f"Fetched position data for index {index}: {position_data}")
        st.write("All Positions Data:", all_positions_data)
    except Exception as e:
        logging.error(f"Error fetching position data: {e}")
        st.error(f"Error fetching position data: {e}")

# Fetch data from both databases using indices 0 to 173
fetch_data_by_index_range(0, 173)
