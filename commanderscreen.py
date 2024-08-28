import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets
student_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1

# โหลดข้อมูลจาก PositionDB
df_positions = pd.DataFrame(position_sheet.get_all_records())
df_positions['PositionID'] = df_positions['PositionID'].astype(str).str.zfill(3)

# Function เพื่อดึงชื่อหน่วยจาก PositionDB โดยอ้างอิงจาก PositionID
def get_position_name(position_id):
    if position_id.isdigit() and len(position_id) == 3:
        position = df_positions[df_positions['PositionID'] == position_id]
        if not position.empty:
            return position.iloc[0]['PositionName']
    return position_id

# Layout ของแอพ Streamlit
st.title("ระบบเลือกที่ลง CGSC102")

# ตั้งค่าเริ่มต้นของ session state เพื่อเก็บข้อมูลที่ใช้ในการแก้ไข
if 'rank_name' not in st.session_state:
    st.session_state['rank_name'] = ""
if 'branch' not in st.session_state:
    st.session_state['branch'] = ""
if 'officer_type' not in st.session_state:
    st.session_state['officer_type'] = ""
if 'other' not in st.session_state:
    st.session_state['other'] = ""
if 'rank' not in st.session_state:
    st.session_state['rank'] = ""
if 'position1' not in st.session_state:
    st.session_state['position1'] = ""
if 'position2' not in st.session_state:
    st.session_state['position2'] = ""
if 'position3' not in st.session_state:
    st.session_state['position3'] = ""

# กล่องค้นหาเพื่อรับรหัสนายทหารนักเรียน
student_id = st.text_input("กรุณาใส่รหัสนายทหารนักเรียน:")

if student_id:
    # โหลดข้อมูลนายทหารนักเรียนใหม่ทุกครั้งที่มีการค้นหา
    df_students = pd.DataFrame(student_sheet.get_all_records())
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

    # ค้นหาข้อมูลนายทหารนักเรียนด้วยรหัสนายทหารนักเรียน
    student_data = df_students[df_students['StudentID'] == student_id.strip()]

    if not student_data.empty:
        # เก็บค่าของฟิลด์ input ไว้ใน session state และดึงชื่อหน่วยตาม Position ID
        student_info = student_data.iloc[0]
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

        position1_name = get_position_name(st.session_state['position1'])
        position2_name = get_position_name(st.session_state['position2'])
        position3_name = get_position_name(st.session_state['position3'])

        # แสดงข้อมูลในตารางแนวตั้งรวมถึงตำแหน่งที่เลือก
        st.write("### ข้อมูลนายทหารนักเรียน")
        st.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
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

    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
