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
            # Searching through the data for the given PositionID
            found = False
            for key, value in data.items():
                if 'PositionID' in value and str(value['PositionID']) == str(position_id):
                    st.write(f"Position data with PositionID {position_id}:")
                    st.json(value)
                    found = True
                    break
            if not found:
                st.write(f"No position found with PositionID {position_id}.")
        else:
            st.write("No data found in the second Firebase database.")
    except Exception as e:
        st.error(f"Error searching for position data: {e}")

# User interface for searching data
st.title("Search Firebase Data")

# Search student by rank
rank_query = st.text_input("Enter Rank to search in the internal-student-db:")
if st.button("Search Student by Rank"):
    if rank_query:
        search_student_by_rank(rank_query)
    else:
        st.error("Please enter a Rank to search.")

# Search position by PositionID
position_id_query = st.text_input("Enter PositionID to search in the internal-position-db:")
if st.button("Search Position by ID"):
    if position_id_query:
        search_position_by_id(position_id_query)
    else:
        st.error("Please enter a PositionID to search.")
