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
        
        # ตรวจสอบและแปลงลิงค์ Google Drive เป็นรูปแบบที่ใช้ได้
        photo_url = student_data.iloc[0]['Photo']
        if "drive.google.com" in photo_url:
            file_id = photo_url.split('/d/')[1].split('/')[0]
            photo_url = f"https://drive.google.com/uc?id={file_id}"

        # แสดงรูปภาพจากลิงค์ในคอลัมน์ Photo
        st.image(photo_url, caption=f"รูปของ {student_data.iloc[0]['RankName']}", use_column_width=True)

        # ใช้ st.write() เพื่อแสดงตารางโดยไม่มี index
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
                        
                        # โหลดข้อมูลใหม่และรีเฟรชตารางที่มีอยู่
                        df_students = pd.DataFrame(student_sheet.get_all_records())
                        df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()
                        updated_student_data = df_students[df_students['StudentID'] == student_id.strip()]
                        
                        # รีเฟรชตารางด้วยข้อมูลที่อัปเดตแล้ว
                        table_placeholder.write(updated_student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)
                        
                        # ล้างสถานะแก้ไขหลังจากอัปเดต
                        st.session_state.clear()
                    except Exception as e:
                        st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
                else:
                    st.error("ไม่พบรหัสนายทหารนักเรียนใน Google Sheet")
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
