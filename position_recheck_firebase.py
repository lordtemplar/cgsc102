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
    try:
        cred1 = credentials.Certificate(firebase_config_1)
        firebase_admin.initialize_app(cred1, {
            'databaseURL': 'https://internal-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except ValueError as e:
        st.error(f"Error initializing the first Firebase app: {e}")

# Check if the second app is already initialized
try:
    app2 = firebase_admin.get_app('second_app')
except ValueError:
    # If the app is not initialized, initialize it
    try:
        cred2 = credentials.Certificate(firebase_config_2)
        app2 = firebase_admin.initialize_app(cred2, {
            'databaseURL': 'https://internal-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
        }, name='second_app')
    except ValueError as e:
        st.error(f"Error initializing the second Firebase app: {e}")

# Function to load data from Firebase into a DataFrame
def load_data_from_firebase(path='/', app=None):
    try:
        ref = db.reference(path, app=app)
        data = ref.get()
        if data is None:
            st.write(f"No data found at the specified path: {path}")
            return pd.DataFrame()  # Return empty DataFrame if no data
        elif isinstance(data, dict):
            # Convert the data into a DataFrame
            st.write(f"Fetched data type: {type(data)}, content: {data}")
            return pd.DataFrame.from_dict(data, orient='index')
        else:
            st.write(f"Data fetched is not in dictionary format; attempting to convert directly to DataFrame.")
            try:
                return pd.DataFrame(data)  # Attempt to handle non-dict format
            except Exception as e:
                st.error(f"Error converting data to DataFrame: {e}")
                return pd.DataFrame()  # Return empty DataFrame in case of error
    except firebase_admin.exceptions.FirebaseError as e:
        st.error(f"Firebase error during data retrieval: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error
    except Exception as e:
        st.error(f"Unexpected error during data retrieval: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of unexpected error

# Load data from both Firebase databases into DataFrames
df1 = load_data_from_firebase('/', app=None)  # Load data from the first Firebase database
df2 = load_data_from_firebase('/', app=app2)  # Load data from the second Firebase database

# Function to fetch data from the loaded DataFrames
def fetch_data_from_dataframe(df, filter_condition=None):
    try:
        if df.empty:
            st.write("The DataFrame is empty. No data to fetch.")
            return df
        if filter_condition:
            # Apply filter condition if provided
            filtered_df = df.query(filter_condition)
            st.write("Filtered data based on the condition:")
            return filtered_df
        else:
            st.write("Fetched data from the DataFrame:")
            return df
    except Exception as e:
        st.error(f"Error fetching data from DataFrame: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Fetch data from the loaded DataFrames
fetched_data1 = fetch_data_from_dataframe(df1)
fetched_data2 = fetch_data_from_dataframe(df2)

# Display data in Streamlit
st.write("Data from the first database:")
st.dataframe(fetched_data1)

st.write("Data from the second database:")
st.dataframe(fetched_data2)
