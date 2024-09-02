import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

# Function to initialize Firebase Admin SDK
def initialize_firebase_app():
    try:
        # Check if Firebase Admin SDK is already initialized
        if not firebase_admin._apps:
            st.write("Initializing Firebase...")
            # Use the JSON service account key file located in the same folder
            cred = credentials.Certificate("positionchoosing-firebase-adminsdk-vr2az-a74f69f4eb.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
            st.write("Firebase initialized successfully.")
        else:
            st.write("Firebase already initialized.")
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        st.stop()

# Function to fetch data from Firebase Realtime Database
def fetch_data_from_firebase():
    try:
        st.write("Attempting to fetch data from Firebase Realtime Database...")
        # Reference to the root node where positions are stored
        ref = db.reference("/")  # Root node to fetch all positions
        data = ref.get()
        if data:
            st.write("Data fetched successfully.")
            # Display each position's details
            for position in data:
                st.write(f"Position ID: {position['PositionID']}")
                st.write(f"Position Name: {position['PositionName']}")
                st.write(f"Unit: {position['Unit']}")
                st.write(f"Specialist: {position['Specialist']}")
                st.write(f"Rank: {position['Rank']}")
                st.write(f"Branch: {position['Branch']}")
                st.write(f"Other: {position['Other']}")
                st.write(f"Status: {position['Status']}")
                st.write("---")  # Separator between records
        else:
            st.write("No data found.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Main script
if __name__ == "__main__":
    st.set_page_config(page_title="Firebase Test")
    st.title("Firebase Connection Test")

    initialize_firebase_app()  # Initialize Firebase connection
    fetch_data_from_firebase()  # Fetch and display data from Firebase
