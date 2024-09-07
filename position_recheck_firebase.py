import streamlit as st
from firebase_admin import db
from 2firebase_connection import initialize_firebase

# Set the title of the Streamlit app
st.set_page_config(page_title="Position Choose")

# Initialize Firebase
app1, app2 = initialize_firebase()

# Function to fetch student data by rank from the first Firebase database
def fetch_student_by_rank(rank):
    try:
        ref = db.reference('/', app=app1)
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'Rank' in value and str(value['Rank']) == str(rank):
                    return key, value  # Return both the key and the student data
        return None, None
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
        return None, None

# Function to update student data in the first Firebase database
def update_student_data(student_key, update_data):
    try:
        ref = db.reference(f"/{student_key}", app=app1)
        ref.update(update_data)
    except Exception as e:
        st.error(f"Error updating student data: {e}")

# Function to fetch position data from the second Firebase database
def fetch_position_data(position_ids):
    try:
        ref = db.reference('/', app=app2)
        data = ref.get()
        matching_positions = {}
        
        # Check if data is a list or dictionary and process accordingly
        if isinstance(data, dict):
            for key, value in data.items():
                if 'PositionID' in value and int(value['PositionID']) in position_ids:
                    matching_positions[int(value['PositionID'])] = value['PositionName']
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'PositionID' in item and int(item['PositionID']) in position_ids:
                    matching_positions[int(item['PositionID'])] = item['PositionName']

        return matching_positions

    except Exception as e:
        st.error(f"Error fetching position data: {e}")
        return {}

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
            'position1': int(student_info['Position1']),
            'position2': int(student_info['Position2']),
            'position3': int(student_info['Position3'])
        })

        # Function to refresh position data
        def refresh_position_data():
            position_ids = [st.session_state['position1'], st.session_state['position2'], st.session_state['position3']]
            return fetch_position_data(position_ids)

        # Fetch and refresh position data
        matching_positions = refresh_position_data()

        # Placeholder for the table to dynamically update
        table_placeholder = st.empty()

        def display_student_info():
            # Display student information with position names in a table format
            table_placeholder.markdown(f"""
            <table>
                <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
                <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
                <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
                <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
                <tr><th>ตำแหน่งลำดับ 1</th><td>{st.session_state['position1']} - {matching_positions.get(st.session_state['position1'], 'N/A')}</td></tr>
                <tr><th>ตำแหน่งลำดับ 2</th><td>{st.session_state['position2']} - {matching_positions.get(st.session_state['position2'], 'N/A')}</td></tr>
                <tr><th>ตำแหน่งลำดับ 3</th><td>{st.session_state['position3']} - {matching_positions.get(st.session_state['position3'], 'N/A')}</td></tr>
            </table>
            """, unsafe_allow_html=True)

        # Display the initial student information
        display_student_info()

        # Input fields for editing positions
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งลำดับ 1", str(st.session_state['position1']))
        position2_input = st.text_input("ตำแหน่งลำดับ 2", str(st.session_state['position2']))
        position3_input = st.text_input("ตำแหน่งลำดับ 3", str(st.session_state['position3']))

        # Validate and update positions
        filled_positions = [position1_input, position2_input, position3_input]
        valid_positions = all(pos.isdigit() for pos in filled_positions)

        if not valid_positions:
            st.error("กรุณากรอกรหัสด้วยตัวเลขอย่างน้อย 1 ตำแหน่งที่เลือก")
        else:
            st.session_state.update({
                'position1': int(position1_input),
                'position2': int(position2_input),
                'position3': int(position3_input)
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

                    # Refresh position data after update
                    matching_positions = refresh_position_data()

                    # Refresh the existing table with new data
                    display_student_info()

                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
