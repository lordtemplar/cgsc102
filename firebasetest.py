import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

# Debug: Print Firebase credentials from secrets
try:
    st.write("Loading Firebase credentials from secrets...")
    firebase_config = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": st.secrets["firebase"]["universe_domain"]
    }

    # Debug: Print the loaded credentials
    st.write("Firebase credentials loaded successfully:")
    st.json(firebase_config)

except Exception as e:
    st.error(f"Error loading Firebase credentials: {e}")
    st.stop()

# Initialize Firebase Admin SDK only once
try:
    if not firebase_admin._apps:
        st.write("Initializing Firebase Admin SDK...")
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://external-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
        st.write("Firebase Admin SDK initialized successfully.")
    else:
        st.write("Firebase Admin SDK is already initialized.")

except ValueError as e:
    st.error(f"ValueError during Firebase initialization: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error during Firebase initialization: {e}")
    st.stop()

# Function to fetch data from Firebase
def get_data(path='/'):
    try:
        st.write(f"Attempting to fetch data from Firebase at path: {path}")
        ref = db.reference(path)
        data = ref.get()
        st.write("Data fetched successfully.")
        return data
    except firebase_admin.exceptions.FirebaseError as e:
        st.error(f"Firebase error during data retrieval: {e}")
    except Exception as e:
        st.error(f"Unexpected error during data retrieval: {e}")

# Fetch data from Firebase
data = get_data('/')
st.write("Data from Firebase:")
st.write(data)
