import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Set the title of the Streamlit app
st.set_page_config(page_title="Position Choose")

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

# Function to fetch student data by rank from the first Firebase database
def fetch_student_by_rank(rank):
    try:
        ref = db.reference('/', firebase_admin.get_app())
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'Rank' in value and str(value['Rank']) == str(rank):
                    return key, value  # Return both the key and the student data
        return None, None
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
        return None, None

# Function to fetch position name from the second Firebase database by position ID
def get_position_name(position_id):
    try:
        ref = db.reference('/', app=app2)
        data = ref.get()
        # Check the data format and retrieve the corresponding PositionName
        if data:
            for key, value in data.items():
                if 'PositionID' in value and value['PositionID'] == position_id:
                    return value['PositionName']
    except Exception as e:
        st.error(f"Error fetching position name: {e}")
    return position_id

# Function to update student data in the first Firebase database
def update_student_data(student_key, update_data):
    try:
        ref = db.reference(f"/{student_key}", firebase_admin.get_app())
        ref.update(update_data)
        st.success("Data successfully updated for the student.")
    except Exception as e:
        st.error(f"Error updating student data: {e}")

# Layout of the Streamlit app
st.title("ระบบเลือกที่ลง CGSC102")

# Initialize session state for storing student data
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# Input box for searching by rank
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

# Check if the search query has changed
if rank_query and rank_query != st.session_state['last_search_query']:
    st.session_state['student_data'] = None
    st.session_state['last_search_query'] = rank_query

if rank_query:
    if st.session_state['student_data'] is None:
        # Fetch student data from Firebase
        student_key, student_data = fetch_student_by_rank(rank_query)
        if student_data:
            st.session_state['student_data'] = student_data
            st.session_state['student_key'] = student_key
        else:
            st.error("ไม่พบข้อมูลที่ค้นหา")
            st.session_state['student_data'] = None

    if st.session_state['student_data'] is not None:
        student_info = st.session_state['student_data']
        st.session_state.update({
            'rank_name': student_info['RankName'],
            'branch': student_info['Branch'],
            'officer_type': student_info['OfficerType'],
            'other': student_info['Other'],
            'rank': str(student_info['Rank']),
            'position1': str(student_info['Position1']).zfill(3),
            'position2': str(student_info['Position2']).zfill(3),
            'position3': str(student_info['Position3']).zfill(3)
        })

        # Fetch position names from Firebase
        position1_name = get_position_name(st.session_state['position1'])
        position2_name = get_position_name(st.session_state['position2'])
        position3_name = get_position_name(st.session_state['position3'])

        # Display data in a table format
        table_placeholder = st.empty()
        table_placeholder.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
            <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
            <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
            <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
            <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
            <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
            <tr><th>ตำแหน่งลำดับ 1</th><td>{position1_name}</td></tr>
            <tr><th>ตำแหน่งลำดับ 2</th><td>{position2_name}</td></tr>
            <tr><th>ตำแหน่งลำดับ 3</th><td>{position3_name}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # Input fields for editing positions
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        position2_input = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        position3_input = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        # Validate and update positions
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

            # Submit button to update data
            if st.button("Submit"):
                try:
                    update_data = {
                        'Position1': st.session_state['position1'],
                        'Position2': st.session_state['position2'],
                        'Position3': st.session_state['position3']
                    }
                    update_student_data(st.session_state['student_key'], update_data)
                    st.success(f"อัปเดตข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_info['StudentID']} สำเร็จแล้ว")

                    # Update displayed table with new data
                    table_placeholder.write(f"""
                    <table>
                        <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
                        <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                        <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                        <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
                        <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
                        <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
                        <tr><th>ตำแหน่งลำดับ 1</th><td>{get_position_name(st.session_state['position1'])}</td></tr>
                        <tr><th>ตำแหน่งลำดับ 2</th><td>{get_position_name(st.session_state['position2'])}</td></tr>
                        <tr><th>ตำแหน่งลำดับ 3</th><td>{get_position_name(st.session_state['position3'])}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
