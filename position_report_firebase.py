# main.py

import streamlit as st
import pandas as pd
from firebase_admin import db
from reportdb_connection import initialize_firebase  # Updated import to reflect the new file name

# Initialize Firebase connections
app1, app2 = initialize_firebase()

# Function to fetch data from Firebase Realtime Databases and load into DataFrames
def fetch_data():
    # Initialize empty DataFrames
    student_df = pd.DataFrame()
    position_df = pd.DataFrame()

    # Fetch data from the first database: confirm-student-db
    try:
        student_data_ref = db.reference('confirm-student-db', app=app1)
        student_data = student_data_ref.get()

        if student_data:
            # Convert student data to DataFrame
            student_df = pd.DataFrame.from_dict(student_data, orient='index')
        else:
            st.warning("ไม่มีข้อมูลนักเรียนในฐานข้อมูลแรก (confirm-student-db).")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูลแรก: {e}")

    # Fetch data from the second database: internal-position-db
    try:
        position_data_ref = db.reference('internal-position-db', app=app2)
        position_data = position_data_ref.get()

        if position_data:
            # Convert position data to DataFrame
            position_df = pd.DataFrame.from_dict(position_data, orient='index')
        else:
            st.warning("ไม่มีข้อมูลตำแหน่งในฐานข้อมูลที่สอง (internal-position-db).")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูลที่สอง: {e}")

    return student_df, position_df

# Function to display data from DataFrames
def display_data(student_df, position_df):
    if not student_df.empty:
        st.header("รายงานข้อมูลนักเรียน (Confirm Student DB)")
        st.dataframe(student_df)  # Display student data DataFrame

    if not position_df.empty:
        st.header("รายงานข้อมูลตำแหน่ง (Internal Position DB)")
        st.dataframe(position_df)  # Display position data DataFrame

# Streamlit app layout
def main():
    st.title("การเลือกตำแหน่งรับราชการ - ระบบรายงาน")
    st.write("หน้านี้แสดงรายงานการเลือกตำแหน่งรับราชการโดยเชื่อมต่อกับฐานข้อมูล Firebase Realtime Database")

    # Button to fetch and display data
    if st.button('ดึงข้อมูลและแสดงรายงาน'):
        student_df, position_df = fetch_data()  # Fetch data and load into DataFrames
        display_data(student_df, position_df)  # Display the data

if __name__ == "__main__":
    main()
