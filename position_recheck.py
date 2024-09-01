import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# ตั้งค่า title bar ของแอพในเบราว์เซอร์
st.set_page_config(page_title="Position Recheck")

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets
student_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1

# ลิงก์สำหรับการอัปเดตข้อมูล
update_link_1 = 'https://docs.google.com/spreadsheets/d/1iOcrhg1qmJ-mT9c3hkpsa1ajyr8riWrZrhL-eO_SCSg'
update_link_2 = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw'

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
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = None
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ""

# กล่องค้นหาเพื่อค้นหาจาก "ลำดับผลการเรียน"
rank_query = st.text_input("กรุณาใส่ลำดับผลการเรียน:")

# ตรวจสอบว่าคำค้นหาใหม่แตกต่างจากคำค้นหาครั้งก่อนหรือไม่
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
            'position1': str(student_info['Position1']).zfill(3),
            'position2': str(student_info['Position2']).zfill(3),
            'position3': str(student_info['Position3']).zfill(3)
        })

        position1_name = get_position_name(st.session_state['position1'])
        position2_name = get_position_name(st.session_state['position2'])
        position3_name = get_position_name(st.session_state['position3'])

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
            <tr><th>ตำแหน่งลำดับ 1</th><td>{position1_name}</td></tr>
            <tr><th>ตำแหน่งลำดับ 2</th><td>{position2_name}</td></tr>
            <tr><th>ตำแหน่งลำดับ 3</th><td>{position3_name}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # กล่องค้นหาเพื่อค้นหาตำแหน่ง
        search_term = st.text_input("ค้นหาตำแหน่ง:")

        if search_term:
            filtered_positions = df_positions[df_positions.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

            if not filtered_positions.empty:
                st.write(f"### ผลการค้นหาสำหรับ \"{search_term}\"")
                for index, row in filtered_positions.iterrows():
                    st.write(f"""
                    <table>
                        <tr><th>รหัสตำแหน่ง</th><td>{row['PositionID']}</td></tr>
                        <tr><th>ชื่อตำแหน่ง</th><td>{row['PositionName']}</td></tr>
                        <tr><th>สังกัด</th><td>{row['Unit']}</td></tr>
                        <tr><th>ชกท.</th><td>{row['Specialist']}</td></tr>
                        <tr><th>อัตรา</th><td>{row['Rank']}</td></tr>
                        <tr><th>เหล่า</th><td>{row['Branch']}</td></tr>
                        <tr><th>หมายเหตุ</th><td>{row['Other']}</td></tr>
                        <tr><th>สถานะ</th><td>{row['Status']}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
            else:
                st.write("ไม่พบตำแหน่งที่ตรงกับการค้นหา")

        # ส่วนกรอกข้อมูลตำแหน่งลำดับ 1, 2, 3
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        position2_input = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        position3_input = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        # ตรวจสอบว่ามีการกรอกข้อมูลอย่างน้อย 1 ตำแหน่งที่ถูกต้อง
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

            # ปุ่ม Submit เพื่ออัพเดทข้อมูล
            if st.button("Submit"):
                try:
                    row_number = student_sheet.find(str(student_info['StudentID'])).row  # ใช้ str() เพื่อให้เป็นประเภทที่ถูกต้อง

                    # อัปเดตข้อมูลไปยังทั้งสองลิงก์ Google Sheets
                    student_sheet.update_cell(row_number, student_sheet.find('Position1').col, st.session_state['position1'])
                    student_sheet.update_cell(row_number, student_sheet.find('Position2').col, st.session_state['position2'])
                    student_sheet.update_cell(row_number, student_sheet.find('Position3').col, st.session_state['position3'])

                    # อัปเดตข้อมูลไปยังลิงก์ที่สอง
                    update_sheet_2 = client.open_by_url(update_link_2).sheet1
                    update_sheet_2.update_cell(row_number, update_sheet_2.find('Position1').col, st.session_state['position1'])
                    update_sheet_2.update_cell(row_number, update_sheet_2.find('Position2').col, st.session_state['position2'])
                    update_sheet_2.update_cell(row_number, update_sheet_2.find('Position3').col, st.session_state['position3'])

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
                        <tr><th>ตำแหน่งลำดับ 1</th><td>{get_position_name(st.session_state['position1'])}</td></tr>
                        <tr><th>ตำแหน่งลำดับ 2</th><td>{get_position_name(st.session_state['position2'])}</td></tr>
                        <tr><th>ตำแหน่งลำดับ 3</th><td>{get_position_name(st.session_state['position3'])}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
