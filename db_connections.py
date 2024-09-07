# db_connections.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase credentials from Streamlit secrets
firebase_config_names = ['firebase1', 'firebase2', 'firebase3', 'firebase4']
firebase_configs = {}

for name in firebase_config_names:
    firebase_configs[name] = {
        "config": {
            "type": st.secrets[name]["type"],
            "project_id": st.secrets[name]["project_id"],
            "private_key_id": st.secrets[name]["private_key_id"],
            "private_key": st.secrets[name]["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets[name]["client_email"],
            "client_id": st.secrets[name]["client_id"],
            "auth_uri": st.secrets[name]["auth_uri"],
            "token_uri": st.secrets[name]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets[name]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets[name]["client_x509_cert_url"],
            "universe_domain": st.secrets[name]["universe_domain"]
        },
        "db_url": f"https://{st.secrets[name]['project_id']}-default-rtdb.asia-southeast1.firebasedatabase.app/"
    }

# Function to initialize Firebase app connections
def initialize_firebase_connections():
    apps = {}
    for key, value in firebase_configs.items():
        try:
            if key not in firebase_admin._apps:
                cred = credentials.Certificate(value['config'])
                app = firebase_admin.initialize_app(cred, {'databaseURL': value['db_url']}, name=key)
                apps[key] = app
        except ValueError as e:
            print(f"Error initializing the Firebase app for {key}: {e}")
    return apps

# Initialize all connections
firebase_apps = initialize_firebase_connections()
