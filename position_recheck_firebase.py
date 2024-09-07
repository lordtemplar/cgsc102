import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# Set the page title in the browser
st.set_page_config(page_title="Debugging: Search and Edit Database")

# Initialize Firebase Admin SDK
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate({
                "type": st.secrets["firebase"]["type"],
                "project_id": st.secrets["firebase"]["project_id"],
                "private_key_id": st.secrets["firebase"]["private_key_id"],
                "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
                "client_email": st.secrets["firebase"]["client_email"],
                "client_id": st.secrets["firebase"]["client_id"],
                "auth_uri": st.secrets["firebase"]["auth_uri"],
                "token_uri": st.secrets["firebase"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
            })
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://internal-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
            st.write("Firebase initialized successfully.")
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")

initialize_firebase()

# Function to load data from Firebase
def fetch_student_data(student_id):
    try:
        ref = db.reference(f"/{student_id}")
        data = ref.get()
        if data:
            st.write(f"Fetched data for Student ID: {student_id}: {data}")
            return data
        else:
            st.write(f"No data found for Student ID: {student_id}.")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to update data in Firebase
def update_student_data(student_id, update_data):
    try:
        ref = db.reference(f"/{student_id}")
        ref.update(update_data)
        st.success(f"Data successfully updated for Student ID: {student_id}.")
    except Exception as e:
        st.error(f"Error updating data: {e}")

# Basic UI for search and edit
st.title("Debugging: Search and Edit Student Data")

# Search box to enter Student ID
student_id = st.text_input("Enter Student ID to search:")

if st.button("Search"):
    if student_id:
        # Fetch data for the given Student ID
        student_data = fetch_student_data(student_id)
        if student_data:
            # Display current data
            st.write("Current Data:")
            st.json(student_data)
            
            # Input fields to edit data
            position1 = st.text_input("Position 1", student_data.get('Position1', ''))
            position2 = st.text_input("Position 2", student_data.get('Position2', ''))
            position3 = st.text_input("Position 3", student_data.get('Position3', ''))
            
            # Update button
            if st.button("Update"):
                update_data = {
                    'Position1': position1,
                    'Position2': position2,
                    'Position3': position3
                }
                update_student_data(student_id, update_data)
    else:
        st.error("Please enter a Student ID to search.")
