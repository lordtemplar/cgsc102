import logging
import streamlit as st
from firebase_admin import db
from firebase_connection import initialize_firebase

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Firebase connections
app1, app2 = initialize_firebase()

def synchronize_databases_by_position_id(position_id):
    """
    Synchronizes data between the two Firebase databases based on PositionID.
    
    Args:
        position_id (str): The PositionID used to identify and synchronize data.
    """
    logging.debug(f"Starting synchronization for PositionID: {position_id}")

    # Fetch data from the first Firebase database (internal-student-db)
    try:
        student_ref = db.reference('/students', app=app1)
        students_data = student_ref.order_by_child('ConfirmedPosition').equal_to(position_id).get()
        logging.debug(f"Fetched students data for PositionID {position_id}: {students_data}")
    except Exception as e:
        logging.error(f"Error fetching student data: {e}")
        st.error(f"Error fetching student data: {e}")
        return

    # Fetch data from the second Firebase database (internal-position-db)
    try:
        position_ref = db.reference(f'/positions/{position_id}', app=app2)
        position_data = position_ref.get()
        logging.debug(f"Fetched position data for PositionID {position_id}: {position_data}")
    except Exception as e:
        logging.error(f"Error fetching position data: {e}")
        st.error(f"Error fetching position data: {e}")
        return

    # Perform synchronization logic here
    if position_data and position_data.get('Status') == 'ว่าง':
        if students_data:
            logging.info(f"Updating position status for PositionID {position_id} to 'ไม่ว่าง'.")
            try:
                position_ref.update({'Status': 'ไม่ว่าง'})
                for student_key, student in students_data.items():
                    student_ref.child(student_key).update({'PositionStatus': 'ไม่ว่าง'})
                    logging.info(f"Updated student {student_key} position status to 'ไม่ว่าง'.")
                st.write(f"Synchronized data for PositionID {position_id}")
            except Exception as e:
                logging.error(f"Error updating data: {e}")
                st.error(f"Error updating data: {e}")
        else:
            logging.debug(f"No students found with ConfirmedPosition {position_id}. No updates made.")
    else:
        logging.debug(f"Position data not found or status already set to 'ไม่ว่าง' for PositionID {position_id}.")

# Example usage
synchronize_databases_by_position_id('001')
