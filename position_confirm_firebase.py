import streamlit as st
from db_connections import firebase_apps  # Import initialized Firebase apps
from firebase_admin import db
import requests

# Set the page configuration at the very beginning
st.set_page_config(page_title="Position Confirm")

# Function to fetch student data by rank from the first Firebase database
def fetch_student_by_rank(rank):
    try:
        ref = db.reference('/', firebase_apps[0])  # Use the first Firebase app
        data = ref.get()

        # Check if data is a dictionary or a list
        if isinstance(data, dict):
            for key, value in data.items():
                if 'Rank' in value and str(value['Rank']) == str(rank):
                    return key, value  # Return both the key and the student data
        elif isinstance(data, list):
            for index, value in enumerate(data):
                if isinstance(value, dict) and 'Rank' in value and str(value['Rank']) == str(rank):
                    return index, value  # Return index (acting as key) and the student data
        return None, None
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
        return None, None

# Function to update data in any Firebase database
def update_database(ref_path, data, firebase_app_index):
    try:
        ref = db.reference(ref_path, firebase_apps[firebase_app_index])
        ref.update(data)
    except Exception as e:
        st.error(f"Error updating database at {ref_path}: {e}")

# Function to fetch position data by PositionID from the second Firebase database
def fetch_position_data_by_id(position_id):
    try:
        ref = db.reference('/', firebase_apps[1])  # Use the second Firebase app
        data = ref.get()
        if isinstance(data, dict):
            for key, value in data.items():
                if 'PositionID' in value and int(value['PositionID']) == position_id:
                    return value  # Return the position data
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'PositionID' in item and int(item['PositionID']) == position_id:
                    return item  # Return the position data
        return None
    except Exception as e:
        st.error(f"Error fetching position data by ID: {e}")
        return None

# Function to send Line Notify message
def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': message}
    requests.post(url, headers=headers, data=data)

# Layout of the Streamlit app
st.title("ระบบเลือกที่ลง CGSC102")

# Initialize session state for storing student data
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""
if 'confirmed_position' not in st.session_state:
    st.session_state['confirmed_position'] = None

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
            matching_positions = {}
            for pos_id in position_ids:
                pos_data = fetch_position_data_by_id(pos_id)
                if pos_data:
                    matching_positions[pos_id] = pos_data['PositionName']
            return matching_positions

        # Fetch and refresh position data
        matching_positions = refresh_position_data()

        # Placeholder for the table to dynamically update
        table_placeholder = st.empty()

        def display_student_info(show_confirmed_only=False):
            if show_confirmed_only and st.session_state['confirmed_position']:
                # Display only the confirmed position
                table_placeholder.markdown(f"""
                <table>
                    <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
                    <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                    <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                    <tr><th>ตำแหน่งที่ยืนยัน</th><td>{st.session_state['confirmed_position']} - {matching_positions.get(st.session_state['confirmed_position'], 'N/A')}</td></tr>
                </table>
                """, unsafe_allow_html=True)
            else:
                # Display full student information with position names
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

        # Dropdown for confirming the selected position
        st.write("### ยืนยัน 'รหัสตำแหน่ง' ที่เลือก")
        confirmed_position = st.selectbox(
            "เลือกตำแหน่งที่ต้องการยืนยัน", 
            options=[
                (st.session_state['position1'], matching_positions.get(st.session_state['position1'], 'N/A')),
                (st.session_state['position2'], matching_positions.get(st.session_state['position2'], 'N/A')),
                (st.session_state['position3'], matching_positions.get(st.session_state['position3'], 'N/A'))
            ], 
            format_func=lambda x: f"{x[0]} - {x[1]}"
        )

        # Button to confirm selection
        if st.button("ยืนยัน"):
            try:
                # Get confirmed position ID and fetch the corresponding position data
                selected_position_id = confirmed_position[0]
                position_data = fetch_position_data_by_id(selected_position_id)
                
                # Fetch student data
                student_data = st.session_state['student_data']
                
                # Prepare data to update
                update_data = {
                    'Branch': student_data['Branch'],
                    'Branch_1': position_data['Branch'] if position_data else None,
                    'OfficerType': student_data['OfficerType'],
                    'Other': student_data['Other'],
                    'PositionID': selected_position_id,
                    'PositionName': position_data['PositionName'] if position_data else None,
                    'Rank': student_data['Rank'],
                    'RankName': position_data['RankName'] if position_data else None,
                    'Rank_1': position_data['Rank'] if position_data else None,
                    'Specialist': position_data['Specialist'] if position_data else None,
                    'StudentID': student_data['StudentID'],
                    'Unit': position_data['Unit'] if position_data else None
                }
        
                # Print update_data for debugging
                st.write("Data to be updated in confirm_student_db:", update_data)
        
                # Update the confirm student database
                update_database(f"/{st.session_state['student_key']}", update_data, 2)
        
                # Update position status in internal and external position databases
                position_key = selected_position_id - 1
                update_database(f"/{position_key}", {'Status': "ไม่ว่าง"}, 1)  # Internal position DB
                update_database(f"/{position_key}", {'Status': "ไม่ว่าง"}, 3)  # External position DB
        
                # Update the internal student database
                update_database(f"/{st.session_state['student_key']}", {'Position1': selected_position_id}, 0)
        
                # Set the confirmed position in session state
                st.session_state['confirmed_position'] = selected_position_id
        
                # Send Line Notify with the new token
                next_rank = int(student_info['Rank']) + 1
                line_token = "snH08HhuKeu11DAgQmyUyYeDcnqgHVlcfRP8Fdqz4db"
                message = f"ลำดับที่ {student_info['Rank']}, รหัสนักเรียน {student_info['StudentID']}, {st.session_state['rank_name']}, เลือกรับราชการในตำแหน่ง {matching_positions[selected_position_id]} ต่อไปเชิญลำดับที่ {next_rank} เลือกที่ลงต่อครับ"
                send_line_notify(message, line_token)
        
                st.success(f"ยืนยันข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_info['StudentID']} สำเร็จแล้ว")
        
                # Refresh the table to show only the confirmed position
                display_student_info(show_confirmed_only=True)
        
            except Exception as e:
                st.error(f"ไม่สามารถยืนยันข้อมูลได้: {e}")

