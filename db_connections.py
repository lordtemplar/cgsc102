# db_connections.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase credentials from Streamlit secrets for the four databases
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

firebase_config_3 = {
    "type": st.secrets["firebase3"]["type"],
    "project_id": st.secrets["firebase3"]["project_id"],
    "private_key_id": st.secrets["firebase3"]["private_key_id"],
    "private_key": st.secrets["firebase3"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase3"]["client_email"],
    "client_id": st.secrets["firebase3"]["client_id"],
    "auth_uri": st.secrets["firebase3"]["auth_uri"],
    "token_uri": st.secrets["firebase3"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase3"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase3"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase3"]["universe_domain"]
}

firebase_config_4 = {
    "type": st.secrets["firebase4"]["type"],
    "project_id": st.secrets["firebase4"]["project_id"],
    "private_key_id": st.secrets["firebase4"]["private_key_id"],
    "private_key": st.secrets["firebase4"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase4"]["client_email"],
    "client_id": st.secrets["firebase4"]["client_id"],
    "auth_uri": st.secrets["firebase4"]["auth_uri"],
    "token_uri": st.secrets["firebase4"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase4"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase4"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase4"]["universe_domain"]
}

# Initialize Firebase Admin SDK for all four databases
def initialize_firebase():
    app1, app2, app3, app4 = None, None, None, None

    # Initialize first Firebase database
    if not firebase_admin._apps:
        try:
            cred1 = credentials.Certificate(firebase_config_1)
            app1 = firebase_admin.initialize_app(cred1, {
                'databaseURL': 'https://internal-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
            st.write("Connected to the first Firebase database (internal-student-db).")
        except ValueError as e:
            st.error(f"Error initializing the first Firebase app: {e}")

    # Initialize second Firebase database
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

    # Initialize third Firebase database
    try:
        app3 = firebase_admin.get_app('third_app')
    except ValueError:
        try:
            cred3 = credentials.Certificate(firebase_config_3)
            app3 = firebase_admin.initialize_app(cred3, {
                'databaseURL': 'https://confirm-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            }, name='third_app')
            st.write("Connected to the third Firebase database (confirm-student-db).")
        except ValueError as e:
            st.error(f"Error initializing the third Firebase app: {e}")

    # Initialize fourth Firebase database
    try:
        app4 = firebase_admin.get_app('fourth_app')
    except ValueError:
        try:
            cred4 = credentials.Certificate(firebase_config_4)
            app4 = firebase_admin.initialize_app(cred4, {
                'databaseURL': 'https://external-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            }, name='fourth_app')
            st.write("Connected to the fourth Firebase database (external-position-db).")
        except ValueError as e:
            st.error(f"Error initializing the fourth Firebase app: {e}")

    return app1, app2, app3, app4

# Initialize all Firebase connections
firebase_apps = initialize_firebase()
