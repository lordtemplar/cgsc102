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
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/edit?usp=drive_link').sheet1

# Layout ของแอพ Streamlit
st.title("ระบบเลือกที่ลง CGSC102")

# ขั้นตอนที่ 1: กล่องค้นหาเพื่อรับรหัสนายทหารนักเรียน
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
        table_placeholder.write(student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)

        # แสดงปุ่มแก้ไขและถัดไป
        col1, col2, _ = st.columns([1, 1, 3])
        
        with col1:
            edit_clicked = st.button("แก้ไข", key="edit_button")
        
        with col2:
            next_clicked = st.button("ถัดไป", key="next_button")
        
        # จัดการการคลิกปุ่มแก้ไข
        if edit_clicked or "edit_mode" in st.session_state:
            st.session_state.edit_mode = True

            # เก็บค่าของฟิลด์ input ไว้ใน session state
            if "rank_name" not in st.session_state:
                st.session_state.rank_name = student_data.iloc[0]['RankName']
            if "branch" not in st.session_state:
                st.session_state.branch = student_data.iloc[0]['Branch']
            if "officer_type" not in st.session_state:
                st.session_state.officer_type = student_data.iloc[0]['OfficerType']
            if "other" not in st.session_state:
                st.session_state.other = student_data.iloc[0]['Other']

            st.write("### แก้ไขข้อมูลนายทหารนักเรียน")
            st.session_state.rank_name = st.text_input("ยศและชื่อ", st.session_state.rank_name)
            st.session_state.branch = st.text_input("เหล่า", st.session_state.branch)
            st.session_state.officer_type = st.text_input("ประเภทนายทหาร", st.session_state.officer_type)
            st.session_state.other = st.text_input("อื่นๆ", st.session_state.other)

            # ปุ่มอัปเดตข้อมูล
            if st.button("อัปเดตข้อมูล", key="update_button"):
                updated_data = [
                    student_id, 
                    st.session_state.rank_name, 
                    st.session_state.branch, 
                    st.session_state.officer_type, 
                    st.session_state.other
                ]
                
                # ค้นหาหมายเลขแถวใน Google Sheet
                cell = student_sheet.find(student_id)
                if cell:
                    row_number = cell.row
                    
                    # อัปเดตแถวใน Google Sheet (อัปเดตเฉพาะคอลัมน์ที่เราสนใจ)
                    try:
                        student_sheet.update(f'A{row_number}:E{row_number}', [updated_data])
                        st.success(f"อัปเดตข้อมูลรหัสนายทหารนักเรียน {student_id} สำเร็จแล้ว")
                        
                        # โหลดใหม่และอัปเดตตารางเดิมด้วยข้อมูลที่รีเฟรช
                        df_students = pd.DataFrame(student_sheet.get_all_records())
                        df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()
                        updated_student_data = df_students[df_students['StudentID'] == student_id.strip()]
                        
                        # รีเฟรชตารางที่มีอยู่ด้วยข้อมูลที่อัปเดตแล้ว
                        table_placeholder.write(updated_student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)

                        # ล้างสถานะแก้ไข
                        st.session_state.clear()
                    except Exception as e:
                        st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
                else:
                    st.error("ไม่พบรหัสนายทหารนักเรียนใน Google Sheet")
        
        # Handle Next button click
        if next_clicked or "next_mode" in st.session_state:
            st.session_state.next_mode = True
            
            # Show all Positions
            st.write("### ตารางตำแหน่งทั้งหมด")
            df_positions = pd.DataFrame(position_sheet.get_all_records())
            df_positions['PositionID'] = df_positions['PositionID'].astype(str).str.zfill(3)  # Ensure PositionID is a 3-digit string
            st.write(df_positions.to_html(index=False), unsafe_allow_html=True)

            # Initialize session state for positions if not already set
            if "position1" not in st.session_state:
                st.session_state.position1 = ""
            if "position2" not in st.session_state:
                st.session_state.position2 = ""
            if "position3" not in st.session_state:
                st.session_state.position3 = ""

            # Input boxes for entering Position IDs
            st.session_state.position1 = st.text_input("ตำแหน่งที่ 1 (ใส่รหัสตำแหน่ง 3 หลัก)", st.session_state.position1).zfill(3)
            st.session_state.position2 = st.text_input("ตำแหน่งที่ 2 (ใส่รหัสตำแหน่ง 3 หลัก)", st.session_state.position2).zfill(3)
            st.session_state.position3 = st.text_input("ตำแหน่งที่ 3 (ใส่รหัสตำแหน่ง 3 หลัก)", st.session_state.position3).zfill(3)

            # Button to submit selections
            if st.button("เลือกที่ลง"):
                try:
                    # Find the row number in the Google Sheet for the student
                    cell = student_sheet.find(student_id)
                    if cell:
                        row_number = cell.row
                        
                        # Update the Google Sheet row with the selected positions
                        student_sheet.update(f'F{row_number}', st.session_state.position1)
                        student_sheet.update(f'G{row_number}', st.session_state.position2)
                        student_sheet.update(f'H{row_number}', st.session_state.position3)
                        
                        st.success("บันทึกข้อมูลที่ลงเรียบร้อยแล้ว")
                    else:
                        st.error("ไม่พบรหัสนายทหารนักเรียนใน Google Sheet")
                except Exception as e:
                    st.error(f"ไม่สามารถบันทึกข้อมูลได้: {e}")
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
