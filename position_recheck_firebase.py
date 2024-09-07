import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import re  # Import regular expressions for rank extraction

# Set the page title in the browser
st.set_page_config(page_title="Position Choose")

# Load Firebase credentials from Streamlit secrets
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
        except ValueError as e:
            st.error(f"Error initializing the first Firebase app: {e}")

    # Initialize second Firebase app only if it hasn't been initialized already
    try:
        firebase_admin.get_app('second_app')
    except ValueError:
        try:
            cred2 = credentials.Certificate(firebase_config_2)
            firebase_admin.initialize_app(cred2, {
                'databaseURL': 'https://internal-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            }, name='second_app')
        except ValueError as e:
            st.error(f"Error initializing the second Firebase app: {e}")

initialize_firebase()

# Function to load data from Firebase into a DataFrame
def load_data_from_firebase(path='/', app=None):
    try:
        ref = db.reference(path, app=app)
        data = ref.get()
        if data is None:
            st.write(f"No data found at the specified path: {path}")
            return pd.DataFrame()
        elif isinstance(data, dict):
            return pd.DataFrame.from_dict(data, orient='index')
        else:
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data from Firebase: {e}")
        return pd.DataFrame()

# Fetch data from both Firebase databases
df_students = load_data_from_firebase('/', app=None)  # Fetch from the first database
df_positions = load_data_from_firebase('/', app=firebase_admin.get_app('second_app'))  # Fetch from the second database
df_positions['PositionID'] = df_positions['PositionID'].astype(str).str.zfill(3)  # Format Position IDs

# Function to fetch student data based on rank
def fetch_student_data(rank_query):
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()
    student_data = df_students[df_students['Rank'].astype(str).str.contains(rank_query.strip(), case=False, na=False)]
    return student_data.iloc[0] if not student_data.empty else None

# Function to get position name from PositionDB by PositionID
def get_position_name(position_id):
    if position_id.isdigit() and len(position_id) == 3:
        position = df_positions[df_positions['PositionID'] == position_id]
        if not position.empty:
            return position.iloc[0]['PositionName']
    return position_id

# Display title
st.title("ระบบเลือกที่ลง CGSC102")

# Initialize session state for student data and search queries
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# Search box to allow user to input the rank
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

# If the search query changes, reset the session state
if rank_query and rank_query != st.session_state['last_search_query']:
    st.session_state['student_data'] = None
    st.session_state['last_search_query'] = rank_query

# Fetch and display student data
if rank_query:
    if st.session_state['student_data'] is None:
        student_data = fetch_student_data(rank_query)
        if student_data is not None:
            st.session_state['student_data'] = student_data
        else:
            st.error("ไม่พบข้อมูลที่ค้นหา")
            st.session_state['student_data'] = None

    if st.session_state['student_data'] is not None:
        student_info = st.session_state['student_data']
        student_id = str(student_info['StudentID']).split(".")[0].strip()

        # Prepare the data for display
        st.session_state.update({
            'rank_name': student_info['RankName'],
            'branch': student_info['Branch'],
            'officer_type': student_info['OfficerType'],
            'other': student_info['Other'],
            'rank': str(student_info['Rank']).strip(),  # Clean up rank value
            'position1': str(student_info['Position1']).zfill(3),
            'position2': str(student_info['Position2']).zfill(3),
            'position3': str(student_info['Position3']).zfill(3)
        })

        # Convert Position IDs to Position Names for Dropdown
        position_id_to_name = {row['PositionID']: row['PositionName'] for index, row in df_positions.iterrows()}

        # Display the dropdown lists with position names
        st.write("### เลือกตำแหน่งจากรายการ")

        position1_name = position_id_to_name.get(st.session_state['position1'], "Unknown Position")
        position2_name = position_id_to_name.get(st.session_state['position2'], "Unknown Position")
        position3_name = position_id_to_name.get(st.session_state['position3'], "Unknown Position")

        # Dropdowns for selecting positions by name
        position1_input = st.selectbox("ตำแหน่งลำดับ 1", list(position_id_to_name.values()), index=list(position_id_to_name.values()).index(position1_name))
        position2_input = st.selectbox("ตำแหน่งลำดับ 2", list(position_id_to_name.values()), index=list(position_id_to_name.values()).index(position2_name))
        position3_input = st.selectbox("ตำแหน่งลำดับ 3", list(position_id_to_name.values()), index=list(position_id_to_name.values()).index(position3_name))

        # Reverse mapping from position name back to ID
        name_to_position_id = {v: k for k, v in position_id_to_name.items()}
        position1_id = name_to_position_id.get(position1_input)
        position2_id = name_to_position_id.get(position2_input)
        position3_id = name_to_position_id.get(position3_input)

        # Update data in Firebase using StudentID as the key
        if st.button("Submit"):
            student_id = format_student_id(st.session_state['student_data']['StudentID'])

            if student_id:  # Ensure student_id is valid
                update_path = f"/{student_id}"  # Construct the path using StudentID
                update_data = {
                    'Position1': position1_id,
                    'Position2': position2_id,
                    'Position3': position3_id
                }
                st.write(f"Updating data for Student ID: {student_id} with data: {update_data}")
                try:
                    ref = db.reference(update_path)
                    ref.update(update_data)
                    st.success(f"Data successfully updated for Student ID: {student_id}.")
                except Exception as e:
                    st.error(f"Failed to update data: {e}")
            else:
                st.error("Invalid Student ID. Cannot update data.")
