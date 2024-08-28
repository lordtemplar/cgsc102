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
            st.session_state['rank'] = student_data.iloc[0]['Rank']
        if "position1" not in st.session_state:
            st.session_state['position1'] = student_data.iloc[0]['Position1']
        if "position2" not in st.session_state:
            st.session_state['position2'] = student_data.iloc[0]['Position2']
        if "position3" not in st.session_state:
            st.session_state['position3'] = student_data.iloc[0]['Position3']

        # แสดงข้อมูลในตารางแนวตั้งรวมถึงตำแหน่งที่เลือก
        table_placeholder.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
            <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
            <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
            <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
            <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
            <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
            <tr><th>ตำแหน่งลำดับ 1</th><td>{st.session_state['position1']}</td></tr>
            <tr><th>ตำแหน่งลำดับ 2</th><td>{st.session_state['position2']}</td></tr>
            <tr><th>ตำแหน่งลำดับ 3</th><td>{st.session_state['position3']}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # กล่องค้นหาเพื่อค้นหาตำแหน่ง
        search_term = st.text_input("ค้นหาตำแหน่ง:")
        
        if search_term:
            df_positions = pd.DataFrame(position_sheet.get_all_records())
            df_positions['PositionID'] = df_positions['PositionID'].astype(str).str.zfill(3)

            # การจับคู่ข้อความกับทุก column
            filtered_positions = df_positions[df_positions.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

            if not filtered_positions.empty:
                st.write(f"### ผลการค้นหาสำหรับ \"{search_term}\"")
                for index, row in filtered_positions.iterrows():
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
        st.session_state['position1'] = st.text_input("ตำแหน่งลำดับ 1", st.session_state['position1'])
        st.session_state['position2'] = st.text_input("ตำแหน่งลำดับ 2", st.session_state['position2'])
        st.session_state['position3'] = st.text_input("ตำแหน่งลำดับ 3", st.session_state['position3'])

        # ปุ่ม Submit เพื่ออัพเดทข้อมูล
        if st.button("Submit"):
            updated_data = [
                student_id, 
                st.session_state['rank_name'], 
                st.session_state['rank'],
                st.session_state['branch'], 
                st.session_state['officer_type'], 
                st.session_state['other'], 
                st.session_state['position1'], 
                st.session_state['position2'], 
                st.session_state['position3']
            ]
            
            # ค้นหาและอัปเดตแถวใน Google Sheet
            try:
                row_number = student_sheet.find(student_id).row
                student_sheet.update(f'A{row_number}:I{row_number}', [updated_data])
                st.success(f"อัปเดตข้อมูลรหัสนายทหารนักเรียน {student_id} สำเร็จแล้ว")

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
                    <tr><th>ตำแหน่งลำดับ 1</th><td>{st.session_state['position1']}</td></tr>
                    <tr><th>ตำแหน่งลำดับ 2</th><td>{st.session_state['position2']}</td></tr>
                    <tr><th>ตำแหน่งลำดับ 3</th><td>{st.session_state['position3']}</td></tr>
                </table>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
