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

# Function เพื่อดึงชื่อหน่วยจาก PositionDB
def get_position_name(position_id):
    position = df_positions[df_positions['PositionID'] == position_id]
    if not position.empty:
        return position.iloc[0]['PositionName']
    return "ยังไม่ได้เลือก"

# Layout ของแอพ Streamlit
st.title("ระบบเลือกที่ลง CGSC102")

# กล่องค้นหาเพื่อรับรหัสนายทหารนักเรียน
student_id = st.text_input("กรุณาใส่รหัสนายทหารนักเรียน:")

if student_id:
    # โหลดข้อมูลนายทหารนักเรียน
    df_students = pd.DataFrame(student_sheet.get_all_records())
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

    # ค้นหาข้อมูลนายทหารนักเรียนด้วยรหัสนายทหารนักเรียน
    student_data = df_students[df_students['StudentID'] == student_id.strip()]

    if not student_data.empty:
        st.write("### ข้อมูลนายทหารนักเรียน")
        table_placeholder = st.empty()

        # เก็บค่าของฟิลด์ input ไว้ใน session state
        if "rank_name" not in st.session_state:
            st.session_state['rank_name'] = student_data.iloc[0]['RankName']
        if "branch" not in st.session_state:
            st.session_state['branch'] = student_data.iloc[0]['Branch']
        if "officer_type" not in st.session_state:
            st.session_state['officer_type'] = student_data.iloc[0]['OfficerType']
        if "other" not in st.session_state:
            st.session_state['other'] = student_data.iloc[0]['Other']
        if "rank" not in st.session_state:
            st.session_state['rank'] = str(student_data.iloc[0]['Rank'])
        if "position1" not in st.session_state:
            st.session_state['position1'] = str(student_data.iloc[0]['Position1'])
        if "position2" not in st.session_state:
            st.session_state['position2'] = str(student_data.iloc[0]['Position2'])
        if "position3" not in st.session_state:
            st.session_state['position3'] = str(student_data.iloc[0]['Position3'])

        # แสดงข้อมูลในตารางแนวตั้งรวมถึงตำแหน่งที่เลือก พร้อมดึงชื่อหน่วยจาก PositionDB
        table_placeholder.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
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

        # ส่วนกรอกข้อมูลตำแหน่งลำดับ 1, 2, 3
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        position2_input = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        position3_input = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        # ตรวจสอบรหัสหน่วยที่กรอกเข้ามาว่ามี 3 หลักหรือไม่
        if len(position1_input) != 3 or not position1_input.isdigit():
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งลำดับ 1")
        elif len(position2_input) != 3 or not position2_input.isdigit():
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งลำดับ 2")
        elif len(position3_input) != 3 or not position3_input.isdigit():
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งลำดับ 3")
        else:
            st.session_state['position1'] = position1_input
            st.session_state['position2'] = position2_input
            st.session_state['position3'] = position3_input

            # ปุ่ม Submit เพื่ออัพเดทข้อมูล
            if st.button("Submit"):
                try:
                    row_number = student_sheet.find(student_id).row

                    # อัปเดตเฉพาะข้อมูล Position1, Position2, Position3 ใน Google Sheets
                    student_sheet.update_cell(row_number, df_students.columns.get_loc('Position1') + 1, st.session_state['position1'])
                    student_sheet.update_cell(row_number, df_students.columns.get_loc('Position2') + 1, st.session_state['position2'])
                    student_sheet.update_cell(row_number, df_students.columns.get_loc('Position3') + 1, st.session_state['position3'])
                    
                    st.success(f"อัปเดตข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_id} สำเร็จแล้ว")
                    
                    # รีเฟรชตารางด้วยข้อมูลที่อัปเดตแล้ว
                    updated_student_data = pd.DataFrame(student_sheet.get_all_records())
                    updated_student_data = updated_student_data[updated_student_data['StudentID'] == student_id.strip()]
                    table_placeholder.write(f"""
                    <table>
                        <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
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
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
