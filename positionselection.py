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
        table_placeholder.write(student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)

        # ปุ่มแก้ไข
        if st.button("แก้ไข"):
            # เก็บค่าของฟิลด์ input ไว้ใน session state
            st.session_state['rank_name'] = st.text_input("ยศและชื่อ", student_data.iloc[0]['RankName'])
            st.session_state['branch'] = st.text_input("เหล่า", student_data.iloc[0]['Branch'])
            st.session_state['officer_type'] = st.text_input("ประเภทนายทหาร", student_data.iloc[0]['OfficerType'])
            st.session_state['other'] = st.text_input("อื่นๆ", student_data.iloc[0]['Other'])

            # ปุ่มอัปเดตข้อมูล
            if st.button("อัปเดตข้อมูล"):
                updated_data = [
                    student_id, 
                    st.session_state['rank_name'], 
                    st.session_state['branch'], 
                    st.session_state['officer_type'], 
                    st.session_state['other']
                ]
                
                # ค้นหาและอัปเดตแถวใน Google Sheet
                try:
                    row_number = student_sheet.find(student_id).row
                    student_sheet.update(f'A{row_number}:E{row_number}', [updated_data])
                    st.success(f"อัปเดตข้อมูลรหัสนายทหารนักเรียน {student_id} สำเร็จแล้ว")

                    # รีเฟรชตารางด้วยข้อมูลที่อัปเดตแล้ว
                    updated_student_data = pd.DataFrame(student_sheet.get_all_records())
                    updated_student_data = updated_student_data[updated_student_data['StudentID'] == student_id.strip()]
                    table_placeholder.write(updated_student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
