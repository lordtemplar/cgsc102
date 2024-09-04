import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import traceback

# Load the environment variable that stores the credentials path
service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

try:
    # Check if the Firebase app is already initialized
    if not firebase_admin._apps:
        st.write("Starting Firebase connection...")

        # Initialize Firebase app with credentials from environment variable
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

        st.write("Firebase Realtime Database connection established successfully.")
    else:
        st.write("Firebase app is already initialized. Using the existing app.")

except Exception as e:
    st.error(f"An error occurred: {traceback.format_exc()}")

# Function to fetch data from Firebase
def fetch_data():
    try:
        st.write("Fetching data from Firebase Realtime Database...")
        ref = db.reference('/')
        data = ref.get()

        if data:
            st.write("Data fetched successfully:", data)
        else:
            st.write("No data found.")

    except Exception as e:
        st.error(f"An error occurred: {traceback.format_exc()}")

if st.button('Fetch Data'):
    fetch_data()
