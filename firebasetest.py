import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Load Firebase credentials from secrets
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

# Ensure Firebase Admin SDK is initialized only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://external-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Correct Database URL
    })

# Function to fetch data from Firebase
def get_data(path='/'):
    ref = db.reference(path)
    data = ref.get()
    return data

# Fetch data from Firebase
data = get_data('/')
st.write(data)
