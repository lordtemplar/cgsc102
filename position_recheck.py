import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import requests  # Import requests to send Line Notify

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

# Function ส่ง Line Notify
def send_line_notify(message, token):
    headers = {
        "Authorization": "Bearer " + token
    }
    payload = {"message": message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)

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

# กล่องค้นหาเพื่อรับรหัสนายทหารนักเรียน
student_id = st.text_input("กรุณาใส่รหัสนายทหารนักเรียน:")

if student_id:
    # โหลดข้อมูลนายทหารนักเรียนใหม่ทุกครั้งที่มีการค้นหา
    df_students = pd.DataFrame(student_sheet.get_all_records())
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

    # Clean the 'Rank' column to ensure all values are numeric
    df_students['Rank'] = pd.to_numeric(df_students['Rank'], errors='coerce')
    df_students = df_students.dropna(subset=['Rank'])  # Drop rows where Rank is NaN

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
            'rank': str(int(student_info['Rank'])),  # Convert to string after ensuring it's an integer
            'position1': str(student_info['Position1']).zfill(3),
        })

        # ตรวจสอบว่าลำดับก่อนหน้าได้เลือกตำแหน่งหรือยัง
        lower_rank_students = df_students[df_students['Rank'] < int(st.session_state['rank'])]
        if lower_rank_students[['Position1']].isnull().any().any():
            st.error("กรุณารอให้ลำดับก่อนหน้าเลือกตำแหน่งก่อน")
        else:
            position1_name = get_position_name(st.session_state['position1'])

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
            </table>
            """, unsafe_allow_html=True)

            # ส่วนกรอกข้อมูลตำแหน่งลำดับ 1
            st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
            position1_input = st.text_input("ตำแหน่งที่เลือก", st.session_state['position1'])

            # ตรวจสอบรหัสหน่วยที่กรอกเข้ามาว่ามี 3 หลักและเป็นตัวเลขหรือไม่
            if len(position1_input) != 3 or not position1_input.isdigit():
                st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งที่เลือก")
            else:
                st.session_state.update({
                    'position1': position1_input.zfill(3),
                })

                # ปุ่ม Submit เพื่ออัพเดทข้อมูล
                if st.button("Submit"):
                    try:
                        row_number = student_sheet.find(student_id).row

                        # อัปเดตเฉพาะข้อมูล Position1 ใน Google Sheets
                        student_sheet.update_cell(row_number, df_students.columns.get_loc('Position1') + 1, st.session_state['position1'])

                        st.success(f"อัปเดตข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_id} สำเร็จแล้ว")

                        # ส่ง Line Notify
                        line_token = "jeFjvSfzdSE6GrSdGNnVbvQRDNeirxnLxRP0Wr5kCni"  # ใช้ token ที่คุณให้มา
                        message = f"รหัสนักเรียน {student_id}, {st.session_state['rank_name']}, เลือกรับราชการในตำแหน่ง {get_position_name(st.session_state['position1'])}"
                        send_line_notify(message, line_token)

                        # รีเฟรชตารางด้วยข้อมูลที่อัปเดตแล้ว
                        updated_student_data = pd.DataFrame(student_sheet.get_all_records())
                        updated_student_data = updated_student_data[updated_student_data['StudentID'] == student_id.strip()]
                        st.write(f"""
                        <table>
                            <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
                            <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                            <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                            <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
                            <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
                            <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
                            <tr><th>ตำแหน่งลำดับ 1</th><td>{get_position_name(st.session_state['position1'])}</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
