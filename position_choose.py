import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# ตั้งค่า title bar ของแอพในเบราว์เซอร์
st.set_page_config(page_title="Position Choose")

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets
student_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1iOcrhg1qmJ-mT9c3hkpsa1ajyr8riWrZrhL-eO_SCSg').sheet1
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1

# ลิงก์สำหรับการอัปเดตข้อมูล
update_link_2 = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw'

# โหลดข้อมูลจาก PositionDB
df_positions = pd.DataFrame(position_sheet.get_all_records())
df_positions['PositionID'] = df_positions['PositionID'].astype(str).str.zfill(3)

# Function เพื่อดึงชื่อหน่วยจาก PositionDB โดยอ้างอิงจาก PositionID
def get_position_name(position_id):
    position = df_positions[df_positions['PositionID'] == position_id]
    return position.iloc[0]['PositionName'] if not position.empty else position_id

# Layout ของแอพ Streamlit
st.title("ระบบเลือกที่ลง CGSC102")

# กำหนดค่าเริ่มต้นของ session state
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# กล่องค้นหาจาก "ลำดับผลการเรียน"
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

# รีเซ็ตข้อมูลหากมีการค้นหาใหม่
if rank_query and rank_query != st.session_state['last_search_query']:
    st.session_state['student_data'] = None
    st.session_state['last_search_query'] = rank_query

if rank_query:
    if st.session_state['student_data'] is None:
        # โหลดข้อมูลนักเรียน
        df_students = pd.DataFrame(student_sheet.get_all_records())
        student_data = df_students[df_students['Rank'].astype(str).str.contains(rank_query.strip(), na=False)]

        if not student_data.empty:
            st.session_state['student_data'] = student_data.iloc[0]
        else:
            st.error("ไม่พบข้อมูลที่ค้นหา")

    if st.session_state['student_data'] is not None:
        student_info = st.session_state['student_data']
        # อัปเดตข้อมูล session state
        for key in ['rank_name', 'branch', 'officer_type', 'other', 'rank', 'position1', 'position2', 'position3']:
            st.session_state[key] = student_info[key.capitalize()] if key in student_info else str(student_info[key.capitalize()]).zfill(3)

        # แสดงข้อมูลนายทหารนักเรียน
        st.write(f"""
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

        # ส่วนกรอกข้อมูลตำแหน่ง
        position1_input = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        position2_input = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        position3_input = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        filled_positions = [position1_input, position2_input, position3_input]
        valid_positions = any(len(pos) == 3 and pos.isdigit() for pos in filled_positions)

        if not valid_positions:
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักอย่างน้อย 1 ตำแหน่งที่เลือก")
        else:
            # อัปเดตข้อมูลตำแหน่งที่เลือก
            if st.button("Submit"):
                try:
                    row_number = student_sheet.find(student_info['StudentID']).row
                    col_positions = { 'Position1': position1_input, 'Position2': position2_input, 'Position3': position3_input }
                    for col, value in col_positions.items():
                        student_sheet.update_cell(row_number, student_sheet.find(col).col, value.zfill(3))
                        update_sheet_2 = client.open_by_url(update_link_2).sheet1
                        update_sheet_2.update_cell(row_number, update_sheet_2.find(col).col, value.zfill(3))

                    st.success(f"อัปเดตข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_info['StudentID']} สำเร็จแล้ว")

                    # รีเฟรชข้อมูลนักเรียน
                    st.session_state['student_data'] = pd.DataFrame(student_sheet.get_all_records()).iloc[row_number - 1]
                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
