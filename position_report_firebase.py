# main.py

import streamlit as st
from firebase_admin import db
from reportdb_connection import initialize_firebase  # Updated import to reflect the new file name

# Initialize Firebase connections
app1, app2 = initialize_firebase()

# Function to fetch and display data from Firebase Realtime Databases
def fetch_and_display_data():
    # Fetch data from the first database: confirm-student-db
    try:
        student_data_ref = db.reference('confirm-student-db', app=app1)
        student_data = student_data_ref.get()

        if student_data:
            st.header("รายงานข้อมูลนักเรียน (Confirm Student DB)")
            for key, value in student_data.items():
                st.subheader(f"รหัสนักเรียน: {key}")
                st.write(value)
        else:
            st.warning("ไม่มีข้อมูลนักเรียนในฐานข้อมูลแรก (confirm-student-db).")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูลแรก: {e}")

    # Fetch data from the second database: internal-position-db
    try:
        position_data_ref = db.reference('internal-position-db', app=app2)
        position_data = position_data_ref.get()

        if position_data:
            st.header("รายงานข้อมูลตำแหน่ง (Internal Position DB)")
            for key, value in position_data.items():
                st.subheader(f"รหัสตำแหน่ง: {key}")
                st.write(value)
        else:
            st.warning("ไม่มีข้อมูลตำแหน่งในฐานข้อมูลที่สอง (internal-position-db).")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูลที่สอง: {e}")

# Streamlit app layout
def main():
    st.title("การเลือกตำแหน่งรับราชการ - ระบบรายงาน")
    st.write("หน้านี้แสดงรายงานการเลือกตำแหน่งรับราชการโดยเชื่อมต่อกับฐานข้อมูล Firebase Realtime Database")

    # Button to fetch and display data
    if st.button('ดึงข้อมูลและแสดงรายงาน'):
        fetch_and_display_data()

if __name__ == "__main__":
    main()
