import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import time

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
        'databaseURL': 'https://external-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Set page title
st.set_page_config(page_title="LIVE Position")

# Initialize search box outside of loop to prevent Duplicate Widget ID
if "search_term" not in st.session_state:
    st.session_state.search_term = st.text_input("ค้นหา ลำดับ, ตำแหน่ง, สังกัด, ชกท., อัตรา, เหล่า หรือ เงื่อนไข")

# Layout of the Streamlit app
st.title("Live Positions")

# Placeholder for updating the table
placeholder = st.empty()

def load_data_and_render_table():
    # Fetch data from Firebase
    try:
        ref = db.reference('/')
        data = ref.get()
        if data is None:
            st.write("No data found.")
            return
        
        # Convert Firebase data to DataFrame
        if isinstance(data, dict):
            df_positions = pd.DataFrame.from_dict(data, orient='index')
        else:
            df_positions = pd.DataFrame(data)
        
        # Format PositionID as 3 digits
        df_positions['PositionID'] = df_positions['PositionID'].apply(lambda x: f"{int(x):03d}")

        # Function to get background color based on Status
        def get_bg_color(status):
            """Function to return background color based on status"""
            return "green" if status == "ว่าง" else "darkred"

        # Function to render the HTML table
        def render_simple_table(data):
            """Function to create and display a simple HTML table"""
            html_table = '<table style="width:100%;">'
            html_table += '<tr><th>ลำดับ</th><th>ตำแหน่ง</th><th>สังกัด</th><th>ชกท.</th><th>อัตรา</th><th>เหล่า</th><th>เงื่อนไข</th></tr>'
            for _, row in data.iterrows():
                bg_color = get_bg_color(row['Status'])
                html_table += f'<tr style="background-color:{bg_color}; color:white;"><td>{row["PositionID"]}</td><td>{row["PositionName"]}</td><td>{row["Unit"]}</td><td>{row["Specialist"]}</td><td>{row["Rank"]}</td><td>{row["Branch"]}</td><td>{row["Other"]}</td></tr>'
            html_table += '</table>'

            # Display the table in the placeholder area
            placeholder.write(html_table, unsafe_allow_html=True)

        # Filter data based on search term
        if st.session_state.search_term:
            filtered_positions = df_positions[df_positions.apply(lambda row: st.session_state.search_term.lower() in str(row['PositionID']).lower() or
                                                                  st.session_state.search_term.lower() in str(row['PositionName']).lower() or
                                                                  st.session_state.search_term.lower() in str(row['Unit']).lower() or
                                                                  st.session_state.search_term.lower() in str(row['Specialist']).lower() or
                                                                  st.session_state.search_term.lower() in str(row['Rank']).lower() or
                                                                  st.session_state.search_term.lower() in str(row['Branch']).lower() or
                                                                  st.session_state.search_term.lower() in str(row['Other']).lower(), axis=1)]
        else:
            filtered_positions = df_positions

        # Render the filtered data
        render_simple_table(filtered_positions)

    except Exception as e:
        st.error(f"Error fetching data from Firebase: {e}")

# Loop to refresh the data every 1 minute
while True:
    load_data_and_render_table()
    time.sleep(60)
