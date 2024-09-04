import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import traceback

# Function to log status messages
def log_status(message):
    st.write(message)  # Display in Streamlit app
    print(message)     # Print to console for debugging

try:
    # Start Firebase connection
    log_status("Starting Firebase connection...")

    # Replace with your Firebase project credentials
    cred = credentials.Certificate('positionchoosing-firebase-adminsdk-vr2az-a74f69f4eb.json')  # Ensure this file is in the same folder or provide the correct path
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Your correct database URL
    })

    log_status("Firebase Realtime Database connection established successfully.")

except Exception as e:
    log_status(f"Error during Firebase initialization: {str(e)}")
    traceback.print_exc()  # Print full error traceback to console

# Function to fetch data from Firebase Realtime Database
def fetch_data():
    try:
        log_status("Fetching data from Firebase Realtime Database...")
        
        # Reference to the database root
        ref = db.reference('/')

        # Fetch the entire data from the root
        data = ref.get()  # Get all data from the root

        if data:
            # Print the entire data structure in the console
            print("Entire data structure:", data)

            # Display the entire data structure in Streamlit
            st.write("Entire data structure:", data)

            log_status("Data fetched and displayed successfully.")
        else:
            log_status("No data found in the database.")

    except Exception as e:
        log_status(f"Error while fetching data: {str(e)}")
        traceback.print_exc()  # Print full error traceback to console

# Button to fetch data in Streamlit
if st.button('Fetch Data'):
    fetch_data()
