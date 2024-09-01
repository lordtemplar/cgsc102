import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import requests

# ตั้งค่า title bar ของแอพในเบราว์เซอร์
st.set_page_config(page_title="Position Choose")

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets ใหม่
student_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1  # ลิงค์ใหม่ที่ให้มา

# ลิงก์สำหรับการอัปเดตข้อมูล
update_link_2 = 'https://docs.google.com/spreadsheets/d/1iOcrhg1qmJ-mT9c3hkpsa1ajyr8riWrZrhL-eO_SCSg'

# โหลดข้อมูลจาก PositionDB ใหม่
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
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)

# Layout ของแอพ Streamlit
st.title("ระบบเลือกที่ลง CGSC102")

# ตั้งค่าเริ่มต้นของ session state เพื่อเก็บข้อมูลที่ใช้ในการแก้ไข
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# กล่องค้นหาเพื่อค้นหาจาก "ลำดับผลการเรียน"
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

if rank_query and rank_query != st.session_state['last_search_query']:
    st.session_state['student_data'] = None  # รีเซ็ตข้อมูล
    st.session_state['last_search_query'] = rank_query  # อัพเดตคำค้นหาใหม่

if rank_query:
    if st.session_state['student_data'] is None:
        # โหลดข้อมูลนักเรียนจาก Google Sheets ครั้งเดียว
        df_students = pd.DataFrame(student_sheet.get_all_records())
        df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

        # ค้นหาข้อมูลนักเรียนด้วย "ลำดับผลการเรียน"
        student_data = df_students[df_students['Rank'].astype(str).str.contains(rank_query.strip(), case=False, na=False)]

        if not student_data.empty:
            st.session_state['student_data'] = student_data.iloc[0]  # เก็บข้อมูลใน session state
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
            'position1': str(student_info['Position1']).zfill(3)
        })

        position1_name = get_position_name(st.session_state['position1'])

        # แสดงข้อมูลในตารางแนวตั้งรวมถึงตำแหน่งที่เลือก
        table_placeholder = st.empty()  # สร้าง placeholder เพื่ออัพเดทตารางเดิม
        table_placeholder.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
            <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
            <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
            <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
            <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
            <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
            <tr><th>ตำแหน่งที่เลือก</th><td>{position1_name}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # ส่วนกรอกข้อมูลตำแหน่งที่เลือก
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งที่เลือก", st.session_state['position1'])

        # ตรวจสอบรหัสหน่วยที่กรอกเข้ามาว่ามี 3 หลักและเป็นตัวเลขหรือไม่
        if len(position1_input) != 3 or not position1_input.isdigit():
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งที่เลือก")
        else:
            st.session_state.update({
                'position1': position1_input.zfill(3)
            })

            # ปุ่ม Confirm เพื่อยืนยันการเลือก
            if st.button("Confirm"):
                try:
                    row_number = student_sheet.find(str(student_info['StudentID'])).row

                    # อัปเดตข้อมูลใน Google Sheets
                    student_sheet.update_cell(row_number, student_sheet.find('Position1').col, st.session_state['position1'])

                    # อัปเดตข้อมูลไปยังลิงก์ที่สอง
                    update_sheet_2 = client.open_by_url(update_link_2).sheet1
                    update_sheet_2.update_cell(row_number, update_sheet_2.find('Position1').col, st.session_state['position1'])

                    # ส่ง Line Notify
                    line_token = "jeFjvSfzdSE6GrSdGNnVbvQRDNeirxnLxRP0Wr5kCni"
                    message = f"รหัสนักเรียน {student_info['StudentID']}, ยศ {st.session_state['rank_name']}, เลือกรับราชการในตำแหน่ง {get_position_name(st.session_state['position1'])}"
                    send_line_notify(message, line_token)

                    st.success(f"อัปเดตข้อมูลตำแหน่งที่เลือกของรหัสนายทหารนักเรียน {student_info['StudentID']} สำเร็จแล้ว")

                    # อัพเดทข้อมูลในตารางเดิมที่แสดงผล
                    table_placeholder.write(f"""
                    <table>
                        <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
                        <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                        <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                        <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
                        <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
                        <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
                        <tr><th>ตำแหน่งที่เลือก</th><td>{get_position_name(st.session_state['position1'])}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
