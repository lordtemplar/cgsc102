import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import requests

# ตั้งค่า title bar ของแอพในเบราว์เซอร์
st.set_page_config(page_title="Position Confirm")

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Client for JSON1
creds_json1 = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client_json1 = gspread.authorize(creds_json1)

# Client for JSON2
creds_json2 = ServiceAccountCredentials.from_json_keyfile_name('soldier-risk-calculator-ebaa5b0e095d.json', scope)
client_json2 = gspread.authorize(creds_json2)

# โหลดข้อมูล Google Sheets ทุกแผ่นงานมาเก็บไว้ในโปรแกรม
internal_student_sheet = client_json1.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/edit?usp=sharing').sheet1
internal_position_sheet = client_json1.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/edit?usp=drive_link').sheet1
confirm_student_sheet = client_json1.open_by_url('https://docs.google.com/spreadsheets/d/1subaqI_b4xj5nKSvDvAkqAVthlRVAavQOy983l-bOn4/edit?usp=drive_link').sheet1
external_position_sheet = client_json2.open_by_url('https://docs.google.com/spreadsheets/d/1N9YSyQ19Gi5roZfgbuo_Bh78CEDHRiVY/edit?usp=sharing&ouid=108880626923731848508&rtpof=true&sd=true').sheet1

# ดึงข้อมูลจาก Google Sheets มาครั้งเดียว
df_internal_students = pd.DataFrame(internal_student_sheet.get_all_records())
df_internal_positions = pd.DataFrame(internal_position_sheet.get_all_records())
df_confirm_students = pd.DataFrame(confirm_student_sheet.get_all_records())
df_external_positions = pd.DataFrame(external_position_sheet.get_all_records())

# จัดการข้อมูลรหัสตำแหน่งและลำดับ
df_internal_positions['PositionID'] = df_internal_positions['PositionID'].astype(str).str.zfill(3)
df_confirm_students['Rank'] = pd.to_numeric(df_confirm_students['Rank'], errors='coerce').dropna().astype(int)

# Function เพื่อดึงชื่อหน่วยจากฐานข้อมูลตำแหน่ง
def get_position_name(position_id):
    if position_id.isdigit() and len(position_id) == 3:
        position = df_internal_positions[df_internal_positions['PositionID'] == position_id]
        if not position.empty:
            return position.iloc[0]['PositionName']
    return position_id

# Function ตรวจสอบสถานะตำแหน่ง
def check_position_availability(position_id):
    internal_position = df_internal_positions[df_internal_positions['PositionID'] == position_id]
    if not internal_position.empty and internal_position.iloc[0]['Status'] == "ไม่ว่าง":
        return False
    return True

# Function ตรวจสอบสถานะการเลือกของลำดับก่อนหน้า
def check_previous_rank_selection(rank):
    if rank == 1:
        return True
    previous_rank_data = df_confirm_students[df_confirm_students['Rank'] == rank - 1]
    if not previous_rank_data.empty and 'Position1' in previous_rank_data.columns and previous_rank_data.iloc[0]['Position1'] == "ยังไม่ได้เลือก":
        return False
    return True

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
    st.session_state['student_data'] = None
    st.session_state['last_search_query'] = rank_query

if rank_query:
    if st.session_state['student_data'] is None:
        student_data = df_internal_students[df_internal_students['Rank'].astype(str).str.contains(rank_query.strip(), case=False, na=False)]
        if not student_data.empty:
            st.session_state['student_data'] = student_data.iloc[0]
        else:
            st.error("ไม่พบข้อมูลที่ค้นหา")
            st.session_state['student_data'] = None

    if st.session_state['student_data'] is not None:
        student_info = st.session_state['student_data']
        rank_number = int(student_info['Rank'])

        if not check_previous_rank_selection(rank_number):
            st.error(f"ลำดับก่อนหน้า (ลำดับ {rank_number - 1}) ยังไม่ได้เลือกตำแหน่ง กรุณารอให้ลำดับก่อนหน้าเลือกก่อน")
        else:
            st.session_state.update({
                'rank_name': student_info['RankName'],
                'branch': student_info['Branch'],
                'officer_type': student_info['OfficerType'],
                'other': student_info['Other'],
                'rank': str(rank_number),
                'position1': str(student_info['Position1']).zfill(3),
                'position2': str(student_info['Position2']).zfill(3),
                'position3': str(student_info['Position3']).zfill(3)
            })

            position1_name = get_position_name(st.session_state['position1'])
            position2_name = get_position_name(st.session_state['position2'])
            position3_name = get_position_name(st.session_state['position3'])

            # แสดงข้อมูลในตารางแนวตั้งรวมถึงตำแหน่งที่เลือก
            table_placeholder = st.empty()
            table_placeholder.write(f"""
            <table>
                <tr><th>รหัสนักเรียน</th><td>{student_info['StudentID']}</td></tr>
                <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
                <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
                <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
                <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
                <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
                <tr><th>ตำแหน่งที่เลือก 1</th><td>{position1_name}</td></tr>
                <tr><th>ตำแหน่งที่เลือก 2</th><td>{position2_name}</td></tr>
                <tr><th>ตำแหน่งที่เลือก 3</th><td>{position3_name}</td></tr>
            </table>
            """, unsafe_allow_html=True)

            # แสดงฟิลด์สำหรับกรอกรหัสตำแหน่ง
            if check_previous_rank_selection(rank_number):
                st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
                position1_input = st.text_input("ตำแหน่งที่เลือก 1", st.session_state['position1'])
                position2_input = st.text_input("ตำแหน่งที่เลือก 2", st.session_state['position2'])
                position3_input = st.text_input("ตำแหน่งที่เลือก 3", st.session_state['position3'])

                valid_positions = all(len(pos) == 3 and pos.isdigit() for pos in [position1_input, position2_input, position3_input])

                if not valid_positions:
                    st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งที่เลือกทั้งหมด")
                else:
                    st.session_state.update({
                        'position1': position1_input.zfill(3),
                        'position2': position2_input.zfill(3),
                        'position3': position3_input.zfill(3)
                    })

                    if st.button("Confirm"):
                        try:
                            # Update ข้อมูลใน DataFrame ก่อน
                            df_confirm_students.loc[df_confirm_students['StudentID'] == student_info['StudentID'], ['Position1', 'Position2', 'Position3']] = \
                                [st.session_state['position1'], st.session_state['position2'], st.session_state['position3']]

                            # อัปเดตข้อมูลกลับไปยัง Google Sheets (ทำครั้งเดียว)
                            confirm_student_sheet.update([df_confirm_students.columns.values.tolist()] + df_confirm_students.values.tolist())

                            # อัปเดตข้อมูลในฐานข้อมูล internal_position_db และ external_position_db
                            internal_position_row = internal_position_sheet.find(st.session_state['position1']).row
                            external_position_row = external_position_sheet.find(st.session_state['position1']).row

                            internal_position_sheet.update_cell(internal_position_row, internal_position_sheet.find('Status').col, "ไม่ว่าง")
                            external_position_sheet.update_cell(external_position_row, external_position_sheet.find('Status').col, "ไม่ว่าง")

                            # ส่ง Line Notify
                            line_token = "jeFjvSfzdSE6GrSdGNnVbvQRDNeirxnLxRP0Wr5kCni"
                            message = f"รหัสนักเรียน {student_info['StudentID']}, {st.session_state['rank_name']}, เลือกรับราชการในตำแหน่ง {get_position_name(st.session_state['position1'])}"
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
                                <tr><th>ตำแหน่งที่เลือก 1</th><td>{get_position_name(st.session_state['position1'])}</td></tr>
                                <tr><th>ตำแหน่งที่เลือก 2</th><td>{get_position_name(st.session_state['position2'])}</td></tr>
                                <tr><th>ตำแหน่งที่เลือก 3</th><td>{get_position_name(st.session_state['position3'])}</td></tr>
                            </table>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
