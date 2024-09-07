import logging
import streamlit as st
from firebase_admin import db
from firebase_connection import initialize_firebase

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Firebase connections
app1, app2 = initialize_firebase()

def fetch_all_data():
    """
    Fetches all data from both Firebase databases.
    """
    # Fetch all data from the first Firebase database (internal-student-db)
    try:
        student_ref = db.reference('/students', app=app1)
        students_data = student_ref.get()
        logging.debug(f"Fetched all student data: {students_data}")
        st.write("All Students Data:", students_data)
    except Exception as e:
        logging.error(f"Error fetching student data: {e}")
        st.error(f"Error fetching student data: {e}")

    # Fetch all data from the second Firebase database (internal-position-db)
    try:
        position_ref = db.reference('/positions', app=app2)
        positions_data = position_ref.get()
        logging.debug(f"Fetched all position data: {positions_data}")
        st.write("All Positions Data:", positions_data)
    except Exception as e:
        logging.error(f"Error fetching position data: {e}")
        st.error(f"Error fetching position data: {e}")

# Fetch all data from both databases
fetch_all_data()
