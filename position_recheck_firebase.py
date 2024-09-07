import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# Set the title bar of the app in the browser
st.set_page_config(page_title="Position Choose")

# Load Firebase credentials from secrets for the first and second databases
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
    except ValueError as e:
        st.error(f"Error initializing the second Firebase app: {e}")

# Function to load all student data from the first Firebase database
def fetch_all_students():
    try:
        ref = db.reference('/', firebase_admin.get_app())
        data = ref.get()
        if data:
            st.write("Fetched all student data from Firebase.")
            return pd.DataFrame.from_dict(data, orient='index')  # Convert to DataFrame for easier processing
        else:
            st.write("No student data found in Firebase.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
        return pd.DataFrame()

# Function to load all position data from the second Firebase database
def fetch_all_positions():
    try:
        ref = db.reference('/', app=app2)
        data = ref.get()
        if data:
            st.write("Fetched all position data from Firebase.")
            if isinstance(data, dict):  # If data is a dictionary
                return pd.DataFrame.from_dict(data, orient='index')
            elif isinstance(data, list):  # If data is a list
                return pd.DataFrame(data)
        else:
            st.write("No position data found in Firebase.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching position data: {e}")
        return pd.DataFrame()

# Function to update student data in the first Firebase database
def update_student_data(student_id, update_data):
    try:
        ref = db.reference(f"/{student_id}", firebase_admin.get_app())
        ref.update(update_data)
        st.success(f"Data successfully updated for Student ID: {student_id}.")
    except Exception as e:
        st.error(f"Error updating student data: {e}")

# Basic UI for search by Rank and edit
st.title("Search by Rank and Edit Student Data")

# Search box to enter Rank
rank_query = st.text_input("Enter Rank to search:")

if st.button("Search by Rank"):
    if rank_query:
        # Fetch all data from Firebase
        df_students = fetch_all_students()
        df_positions = fetch_all_positions()
        if not df_students.empty:
            # Filter data based on rank
            student_data = df_students[df_students['Rank'].astype(str) == rank_query.strip()]
            
            if not student_data.empty:
                # Display current data
                st.write("Current Data:")
                st.json(student_data.to_dict(orient='records')[0])  # Display the first match
                
                # Extract Student ID from the first match
                student_id = student_data.index[0]
                
                # Create a dictionary to map PositionID to PositionName
                position_id_to_name = {}
                for index, row in df_positions.iterrows():
                    position_id_to_name[row['PositionID']] = row['PositionName']

                # Input fields to edit data
                position1 = st.text_input("Position 1", student_data.iloc[0].get('Position1', ''))
                position2 = st.text_input("Position 2", student_data.iloc[0].get('Position2', ''))
                position3 = st.text_input("Position 3", student_data.iloc[0].get('Position3', ''))
                
                # Display position names based on IDs
                st.write(f"Position 1 Name: {position_id_to_name.get(position1, 'Unknown')}")
                st.write(f"Position 2 Name: {position_id_to_name.get(position2, 'Unknown')}")
                st.write(f"Position 3 Name: {position_id_to_name.get(position3, 'Unknown')}")
                
                # Update button
                if st.button("Update"):
                    update_data = {
                        'Position1': position1,
                        'Position2': position2,
                        'Position3': position3
                    }
                    update_student_data(student_id, update_data)
            else:
                st.write("No student found with the provided Rank.")
        else:
            st.write("No student data available to search.")
    else:
        st.error("Please enter a Rank to search.")
