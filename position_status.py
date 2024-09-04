import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import traceback

# Function to log status messages
def log_status(message):
    st.write(message)  # Display in Streamlit app
    print(message)     # Print to console for debugging

try:
    # Check if the Firebase app is already initialized
    if not firebase_admin._apps:
        log_status("Starting Firebase connection...")

        # Replace with your new Firebase project credentials
        cred = credentials.Certificate('positionchoosing-ffdfc3920e83.json')  # Update this with the new JSON file path
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Your correct database URL
        })

        log_status("Firebase Realtime Database connection established successfully.")
    else:
        log_status("Firebase app is already initialized. Using the existing app.")

except Exception as e:
    log_status(f"Error during Firebase initialization: {str(e)}")
    st.error(f"An error occurred: {traceback.format_exc()}")  # Display the traceback in Streamlit

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
        st.error(f"An error occurred: {traceback.format_exc()}")  # Display the traceback in Streamlit

# Button to fetch data in Streamlit
if st.button('Fetch Data'):
    fetch_data()
