import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Set the title of the Streamlit app
st.set_page_config(page_title="Firebase Data Viewer")

# Load Firebase credentials from Streamlit secrets for the first and second databases
firebase_config_1 = {
    "type": st.secrets["firebase1"]["type"],
    "project_id": st.secrets["firebase1"]["project_id"],
    "private_key_id": st.secrets["firebase1"]["private_key_id"],
    "private_key": st.secrets["firebase1"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase1"]["client_email"],
    "client_id": st.secrets["firebase1"]["client_id"],
    "auth_uri": st.secrets["firebase1"]["auth_uri"],
    "token_uri": st.secrets["firebase1"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase1"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase1"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase1"]["universe_domain"]
}

firebase_config_2 = {
    "type": st.secrets["firebase2"]["type"],
    "project_id": st.secrets["firebase2"]["project_id"],
    "private_key_id": st.secrets["firebase2"]["private_key_id"],
    "private_key": st.secrets["firebase2"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase2"]["client_email"],
    "client_id": st.secrets["firebase2"]["client_id"],
    "auth_uri": st.secrets["firebase2"]["auth_uri"],
    "token_uri": st.secrets["firebase2"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase2"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase2"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase2"]["universe_domain"]
}

# Initialize Firebase Admin SDK for both databases
if not firebase_admin._apps:
    try:
        cred1 = credentials.Certificate(firebase_config_1)
        firebase_admin.initialize_app(cred1, {
            'databaseURL': 'https://internal-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
        st.write("Connected to the first Firebase database (internal-student-db).")
    except ValueError as e:
        st.error(f"Error initializing the first Firebase app: {e}")

try:
    app2 = firebase_admin.get_app('second_app')
except ValueError:
    try:
        cred2 = credentials.Certificate(firebase_config_2)
        app2 = firebase_admin.initialize_app(cred2, {
            'databaseURL': 'https://internal-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
        }, name='second_app')
        st.write("Connected to the second Firebase database (internal-position-db).")
    except ValueError as e:
        st.error(f"Error initializing the second Firebase app: {e}")

# Initialize session state variables
if 'student_data' not in st.session_state:
    st.session_state.student_data = {}
if 'position_data' not in st.session_state:
    st.session_state.position_data = {}

# Function to search for student data by rank in the first Firebase database
def search_student_by_rank(rank):
    try:
        ref = db.reference('/', firebase_admin.get_app())
        data = ref.get()
        if data:
            # Searching through the data for the given rank
            found = False
            for key, value in data.items():
                if 'Rank' in value and str(value['Rank']) == str(rank):
                    st.write(f"Student data with Rank {rank}:")
                    st.json(value)
                    found = True

                    # Store the fetched data in session state
                    st.session_state.student_data = {
                        'key': key,
                        'RankName': value.get('RankName', ''),
                        'Branch': value.get('Branch', ''),
                        'OfficerType': value.get('OfficerType', ''),
                        'Position1': value.get('Position1', ''),
                        'Position2': value.get('Position2', ''),
                        'Position3': value.get('Position3', ''),
                        'Other': value.get('Other', ''),
                        'StudentID': value.get('StudentID', '')
                    }
                    break
            if not found:
                st.write(f"No student found with Rank {rank}.")
        else:
            st.write("No data found in the first Firebase database.")
    except Exception as e:
        st.error(f"Error searching for student data: {e}")

# Function to search for position data by PositionID in the second Firebase database
def search_position_by_id(position_id):
    try:
        ref = db.reference('/', app=app2)
        data = ref.get()
        if data:
            # Check if the data is a dictionary or a list
            if isinstance(data, dict):
                # Handle the dictionary format
                found = False
                for key, value in data.items():
                    if 'PositionID' in value and str(value['PositionID']) == str(position_id):
                        st.write(f"Position data with PositionID {position_id}:")
                        st.json(value)
                        found = True

                        # Store the fetched data in session state
                        st.session_state.position_data = {
                            'key': key,
                            'PositionName': value.get('PositionName', ''),
                            'Branch': value.get('Branch', ''),
                            'Other': value.get('Other', ''),
                            'Specialist': value.get('Specialist', ''),
                            'Status': value.get('Status', ''),
                            'Unit': value.get('Unit', '')
                        }
                        break
                if not found:
                    st.write(f"No position found with PositionID {position_id}.")
            elif isinstance(data, list):
                # Handle the list format
                found = False
                for index, item in enumerate(data):
                    if isinstance(item, dict) and 'PositionID' in item and str(item['PositionID']) == str(position_id):
                        st.write(f"Position data with PositionID {position_id}:")
                        st.json(item)
                        found = True

                        # Store the fetched data in session state
                        st.session_state.position_data = {
                            'key': str(index),
                            'PositionName': item.get('PositionName', ''),
                            'Branch': item.get('Branch', ''),
                            'Other': item.get('Other', ''),
                            'Specialist': item.get('Specialist', ''),
                            'Status': item.get('Status', ''),
                            'Unit': item.get('Unit', '')
                        }
                        break
                if not found:
                    st.write(f"No position found with PositionID {position_id}.")
            else:
                st.write("Unexpected data format received from Firebase.")
        else:
            st.write("No data found in the second Firebase database.")
    except Exception as e:
        st.error(f"Error searching for position data: {e}")

# Function to update student data in the first Firebase database
def update_student_data(student_key, update_data):
    try:
        ref = db.reference(f"/{student_key}", firebase_admin.get_app())
        ref.update(update_data)
        st.success(f"Data successfully updated for Student with key {student_key}.")
    except Exception as e:
        st.error(f"Error updating student data: {e}")

# Function to update position data in the second Firebase database
def update_position_data(position_key, update_data):
    try:
        ref = db.reference(f"/{position_key}", app=app2)
        ref.update(update_data)
        st.success(f"Data successfully updated for Position with key {position_key}.")
    except Exception as e:
        st.error(f"Error updating position data: {e}")

# User interface for searching data
st.title("Search and Edit Firebase Data")

# Search student by rank
rank_query = st.text_input("Enter Rank to search in the internal-student-db:")
if st.button("Search Student by Rank"):
    if rank_query:
        search_student_by_rank(rank_query)
    else:
        st.error("Please enter a Rank to search.")

# Display editable fields if student data is loaded
if 'student_data' in st.session_state and st.session_state.student_data:
    st.write("### Edit Student Data")
    student_key = st.session_state.student_data['key']
    updated_rank_name = st.text_input("RankName", st.session_state.student_data['RankName'])
    updated_branch = st.text_input("Branch", st.session_state.student_data['Branch'])
    updated_officer_type = st.text_input("OfficerType", st.session_state.student_data['OfficerType'])
    updated_position1 = st.text_input("Position1", st.session_state.student_data['Position1'])
    updated_position2 = st.text_input("Position2", st.session_state.student_data['Position2'])
    updated_position3 = st.text_input("Position3", st.session_state.student_data['Position3'])
    updated_other = st.text_input("Other", st.session_state.student_data['Other'])
    updated_student_id = st.text_input("StudentID", st.session_state.student_data['StudentID'])

    if st.button("Update Student Data"):
        update_data = {
            'RankName': updated_rank_name,
            'Branch': updated_branch,
            'OfficerType': updated_officer_type,
            'Position1': updated_position1,
            'Position2': updated_position2,
            'Position3': updated_position3,
            'Other': updated_other,
            'StudentID': updated_student_id
        }
        update_student_data(student_key, update_data)

# Search position by PositionID
position_id_query = st.text_input("Enter PositionID to search in the internal-position-db:")
if st.button("Search Position by ID"):
    if position_id_query:
        search_position_by_id(position_id_query)
    else:
        st.error("Please enter a PositionID to search.")

# Display editable fields if position data is loaded
if 'position_data' in st.session_state and st.session_state.position_data:
    st.write("### Edit Position Data")
    position_key = st.session_state.position_data['key']
    updated_position_name = st.text_input("PositionName", st.session_state.position_data['PositionName'])
    updated_branch = st.text_input("Branch", st.session_state.position_data['Branch'])
    updated_other = st.text_input("Other", st.session_state.position_data['Other'])
    updated_specialist = st.text_input("Specialist", st.session_state.position_data['Specialist'])
    updated_status = st.text_input("Status", st.session_state.position_data['Status'])
    updated_unit = st.text_input("Unit", st.session_state.position_data['Unit'])

    if st.button("Update Position Data"):
        update_data = {
            'PositionName': updated_position_name,
            'Branch': updated_branch,
            'Other': updated_other,
            'Specialist': updated_specialist,
            'Status': updated_status,
            'Unit': updated_unit
        }
        update_position_data(position_key, update_data)
