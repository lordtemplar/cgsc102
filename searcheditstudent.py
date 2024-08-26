import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheets
student_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1

# Streamlit App Layout
st.title("ค้นหาและแก้ไขข้อมูลนายทหารนักเรียน")

# Step 1: Input box to get Student ID
student_id = st.text_input("กรุณาใส่รหัสนายทหารนักเรียน:")

if student_id:
    # Load student data
    df_students = pd.DataFrame(student_sheet.get_all_records())
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

    # Find the student data by Student ID
    student_data = df_students[df_students['StudentID'] == student_id.strip()]

    if not student_data.empty:
        st.write("### ข้อมูลนายทหารนักเรียน")
        st.table(student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']])

        # Edit fields
        st.write("### แก้ไขข้อมูลนายทหารนักเรียน")
        rank_name = st.text_input("ยศและชื่อ", student_data.iloc[0]['RankName'])
        branch = st.text_input("เหล่า", student_data.iloc[0]['Branch'])
        officer_type = st.text_input("ประเภทนายทหาร", student_data.iloc[0]['OfficerType'])
        other = st.text_input("อื่นๆ", student_data.iloc[0]['Other'])

        # Update button
        if st.button("อัปเดตข้อมูล"):
            updated_data = [student_id, rank_name, branch, officer_type, other]
            
            # Find the row number in the Google Sheet
            cell = student_sheet.find(student_id)
            if cell:
                row_number = cell.row
                
                # Update the Google Sheet row
                try:
                    student_sheet.update(f'A{row_number}:E{row_number}', [updated_data])
                    st.success(f"อัปเดตข้อมูลรหัสนายทหารนักเรียน {student_id} สำเร็จแล้ว")
                    
                    # Reload and display updated data
                    df_students = pd.DataFrame(student_sheet.get_all_records())
                    updated_student_data = df_students[df_students['StudentID'] == student_id.strip()]
                    
                    st.write("### ข้อมูลนายทหารนักเรียนที่อัปเดตแล้ว")
                    st.table(updated_student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']])
                except Exception as e:
                    st.error(f"ไม่สามารถอัปเดตข้อมูลได้: {e}")
            else:
                st.error("ไม่พบรหัสนายทหารนักเรียนใน Google Sheet")
    else:
        st.error("ไม่พบรหัสนายทหารนักเรียน")
