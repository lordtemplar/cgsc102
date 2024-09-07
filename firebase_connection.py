# firebase_connection.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

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
def initialize_firebase():
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
    return firebase_admin.get_app(), firebase_admin.get_app('second_app')
