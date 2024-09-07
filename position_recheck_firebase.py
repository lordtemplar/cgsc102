import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# Load Firebase credentials from secrets for the first database
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

# Load Firebase credentials from secrets for the second database
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

# Initialize Firebase Admin SDK for the first database
if not firebase_admin._apps:
    cred1 = credentials.Certificate(firebase_config_1)
    firebase_admin.initialize_app(cred1, {
        'databaseURL': 'https://internal-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Initialize Firebase Admin SDK for the second database as a named app
cred2 = credentials.Certificate(firebase_config_2)
app2 = firebase_admin.initialize_app(cred2, {
    'databaseURL': 'https://internal-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
}, name='second_app')

# Function to fetch data from the first Firebase database
def fetch_data_from_first_db(path='/'):
    try:
        ref = db.reference(path)
        data = ref.get()
        if data is None:
            st.write("No data found at the specified path in the first database.")
            return pd.DataFrame()  # Return empty DataFrame if no data
        else:
            # Convert the data into a DataFrame
            return pd.DataFrame.from_dict(data, orient='index')
    except firebase_admin.exceptions.FirebaseError as e:
        st.error(f"Firebase error during data retrieval from the first database: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Function to fetch data from the second Firebase database
def fetch_data_from_second_db(path='/'):
    try:
        ref = db.reference(path, app=app2)
        data = ref.get()
        if data is None:
            st.write("No data found at the specified path in the second database.")
            return pd.DataFrame()  # Return empty DataFrame if no data
        else:
            # Convert the data into a DataFrame
            return pd.DataFrame.from_dict(data, orient='index')
    except firebase_admin.exceptions.FirebaseError as e:
        st.error(f"Firebase error during data retrieval from the second database: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Fetch data from both databases
df1 = fetch_data_from_first_db('/')
df2 = fetch_data_from_second_db('/')

st.write("Data from the first database:")
st.dataframe(df1)

st.write("Data from the second database:")
st.dataframe(df2)
