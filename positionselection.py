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

# Layout ของแอพ Streamlit
st.title("ระบบเลือกที่ลง CGSC102")

# กล่องค้นหาเพื่อรับรหัสนายทหารนักเรียน
student_id = st.text_input("กรุณาใส่รหัสนายทหารนักเรียน:")

if student_id:
    # โหลดข้อมูลนักเรียนใหม่ทุกครั้งที่มีการค้นหา
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
            'position1': str(student_info['Position1']),
            'position2': str(student_info['Position2']),
            'position3': str(student_info['Position3'])
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

        # กล่องค้นหาเพื่อค้นหาตำแหน่ง
        search_term = st.text_input("ค้นหาตำแหน่ง:")
        
        if search_term:
            filtered_positions = df_positions[df_positions.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

            if not filtered_positions.empty:
                st.write(f"### ผลการค้นหาสำหรับ \"{search_term}\"")
                for _, row in filtered_positions.iterrows():
                    st.write(f"""
                    <table>
                        <tr><th>รหัสตำแหน่ง</th><td>{row['PositionID']}</td></tr>
                        <tr><th>ตำแหน่ง</th><td>{row['PositionName']}</td></tr>
                        <tr><th>ชกท.</th><td>{row['Unit']}</td></tr>
                        <tr><th>อัตรา</th><td>{row['Specialist']}</td></tr>
                        <tr><th>เหล่า</th><td>{row['Branch']}</td></tr>
                        <tr><th>อื่นๆ</th><td>{row['Other']}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
            else:
                st.write("ไม่พบตำแหน่งที่ตรงกับการค้นหา")

        # ส่วนกรอกข้อมูลตำแหน่งลำดับ 1, 2, 3
        st.write("### กรอก 'รหัสตำแหน่ง' ที่เลือก")
        position1_input = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        position2_input = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        position3_input = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        # ตรวจสอบรหัสหน่วยที่กรอกเข้ามาว่ามี 3 หลักหรือไม่
        valid_positions = all(len(pos) == 3 and pos.isdigit() for pos in [position1_input, position2_input, position3_input])

        if not valid_positions:
            st.error("กรุณากรอกรหัสด้วยเลข 3 หลักสำหรับตำแหน่งที่เลือกทั้งหมด")
        else:
            st.session_state.update({
                'position1': position1_input,
                'position2': position2_input,
                'position3': position3_input
            })

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
                    st.write(f"""
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
