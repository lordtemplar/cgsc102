import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

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

# Initialize Firebase Admin SDK only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://internal-student-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Function to fetch data from Firebase
def fetch_data_to_dataframe(path='/'):
    try:
        st.write(f"Fetching data from Firebase at path: {path}")
        ref = db.reference(path)
        data = ref.get()

        if data is None:
            st.write("No data found at the specified path.")
            return pd.DataFrame()  # Return empty DataFrame if no data
        else:
            # Convert the data into a DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame.from_dict(data, orient='index')  # Convert dict to DataFrame
                st.write("Data fetched successfully and converted to DataFrame:")
                st.dataframe(df)  # Display DataFrame in Streamlit
                return df
            else:
                st.write("Data is not in dictionary format, converting directly to DataFrame.")
                df = pd.DataFrame(data)  # Handle non-dict format
                st.dataframe(df)
                return df

    except firebase_admin.exceptions.FirebaseError as e:
        st.error(f"Firebase error during data retrieval: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error
    except Exception as e:
        st.error(f"Unexpected error during data retrieval: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Fetch data from Firebase and convert to DataFrame
dataframe = fetch_data_to_dataframe('/')
