import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# Set the title bar of the app in the browser
st.set_page_config(page_title="Position Choose")

# Load Firebase credentials from secrets for the first and second databases
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
            st.write("Firebase app 1 initialized successfully.")
        except ValueError as e:
            st.error(f"Error initializing the first Firebase app: {e}")

    try:
        firebase_admin.get_app('second_app')
    except ValueError:
        try:
            cred2 = credentials.Certificate(firebase_config_2)
            firebase_admin.initialize_app(cred2, {
                'databaseURL': 'https://internal-position-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            }, name='second_app')
            st.write("Firebase app 2 initialized successfully.")
        except ValueError as e:
            st.error(f"Error initializing the second Firebase app: {e}")

initialize_firebase()

# Function to load data from Firebase into DataFrame
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

# Helper function to update Firebase database
def update_firebase_data(path, data, app=None):
    try:
        ref = db.reference(path, app=app)
        ref.update(data)
        st.success(f"Data successfully updated at {path}.")
    except Exception as e:
        st.error(f"Failed to update data at {path}: {e}")

# Helper function to handle student ID conversion
def format_student_id(student_id):
    try:
        # Remove any decimal point and convert to string
        return str(student_id).split(".")[0].strip()
    except Exception as e:
        st.error(f"Error formatting student ID: {e}")
        return ""

# Helper function to fetch student data
def fetch_student_data(rank_query):
    # Search for student data by "Rank"
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()
    student_data = df_students[df_students['Rank'].astype(str).str.contains(rank_query.strip(), case=False, na=False)]
    return student_data.iloc[0] if not student_data.empty else None

# Load data from both Firebase databases into DataFrames
df_students = load_data_from_firebase('/', app=None)  # Load data from the first Firebase database
df_positions = load_data_from_firebase('/', app=firebase_admin.get_app('second_app'))  # Load data from the second Firebase database

# Ensure PositionID is in the correct format
df_positions['PositionID'] = df_positions['PositionID'].astype(str).str.zfill(3)

# Function to get position name from PositionDB by PositionID
def get_position_name(position_id):
    if position_id.isdigit() and len(position_id) == 3:
        position = df_positions[df_positions['PositionID'] == position_id]
        if not position.empty:
            return position.iloc[0]['PositionName']
    return position_id

# Streamlit App Layout
st.title("ระบบเลือกที่ลง CGSC102")

# Initialize session state
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# Search box to search by "Rank"
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

# Check if the new search query is different from the last one
if rank_query and rank_query != st.session_state['last_search_query']:
    st.session_state['student_data'] = None
    st.session_state['last_search_query'] = rank_query

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
        student_id = format_student_id(student_info['StudentID'])
        rank = str(student_info['Rank'])  # Use the Rank as a key for updating

        st.session_state.update({
            'rank_name': student_info['RankName'],
            'branch': student_info['Branch'],
            'officer_type': student_info['OfficerType'],
            'other': student_info['Other'],
            'rank': rank,
            'position1': str(student_info['Position1']).zfill(3),
            'position2': str(student_info['Position2']).zfill(3),
            'position3': str(student_info['Position3']).zfill(3)
        })

        position1_name = get_position_name(st.session_state['position1'])
        position2_name = get_position_name(st.session_state['position2'])
        position3_name = get_position_name(st.session_state['position3'])

        # Display student information
        table_placeholder = st.empty()
        table_placeholder.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
            <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
            <tr><th>ลำดับ</th><td>{rank}</td></tr>
            <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
            <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
            <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
            <tr><th>ตำแหน่งลำดับ 1</th><td>{position1_name}</td></tr>
            <tr><th>ตำแหน่งลำดับ 2</th><td>{position2_name}</td></tr>
            <tr><th>ตำแหน่งลำดับ 3</th><td>{position3_name}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # Input fields for updating positions
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        position2_input = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        position3_input = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        filled_positions = [position1_input, position2_input, position3_input]
        valid_positions = any(len(pos) == 3 and pos.isdigit() for pos in filled_positions)

        if not valid_positions:
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักอย่างน้อย 1 ตำแหน่งที่เลือก")
        else:
            st.session_state.update({
                'position1': position1_input.zfill(3),
                'position2': position2_input.zfill(3),
                'position3': position3_input.zfill(3)
            })

            # Submit button to update data in Firebase
            if st.button("Submit"):
                # Use the Rank as the key to update the correct place
                update_path = f"/{rank}"
                update_data = {
                    'Position1': st.session_state['position1'],
                    'Position2': st.session_state['position2'],
                    'Position3': st.session_state['position3']
                }
                st.write(f"Updating data at path: {update_path} with data: {update_data}")
                update_firebase_data(update_path, update_data)
