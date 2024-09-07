# main.py

import streamlit as st
import pandas as pd
from firebase_admin import db
from reportdb_connection import initialize_firebase  # Import connection script

# Initialize Firebase connections
app1, app2 = initialize_firebase()

# Function to fetch data from Firebase Realtime Databases and load into DataFrames
def fetch_data():
    # Initialize empty DataFrames
    student_df = pd.DataFrame()
    position_df = pd.DataFrame()

    # Fetch data from the first database: confirm-student-db
    try:
        # Reference the root node containing the entries
        student_data_ref = db.reference('/', app=app1)
        student_data = student_data_ref.get()

        # Check if the fetched data is a list or dictionary
        if isinstance(student_data, list):
            # Convert list of dictionaries to DataFrame
            student_df = pd.DataFrame(student_data)
        elif isinstance(student_data, dict):
            # Convert dictionary to DataFrame
            student_df = pd.DataFrame.from_dict(student_data, orient='index')
        else:
            st.warning("ไม่มีข้อมูลนักเรียนในฐานข้อมูลแรก (confirm-student-db).")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูลแรก: {e}")

    # Fetch data from the second database: internal-position-db
    try:
        # Reference the root node containing the entries
        position_data_ref = db.reference('/', app=app2)
        position_data = position_data_ref.get()

        # Check if the fetched data is a list or dictionary
        if isinstance(position_data, list):
            # Convert list of dictionaries to DataFrame
            position_df = pd.DataFrame(position_data)
        elif isinstance(position_data, dict):
            # Convert dictionary to DataFrame
            position_df = pd.DataFrame.from_dict(position_data, orient='index')
        else:
            st.warning("ไม่มีข้อมูลตำแหน่งในฐานข้อมูลที่สอง (internal-position-db).")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูลที่สอง: {e}")

    return student_df, position_df

# Function to display data from DataFrames
def display_data(student_df, position_df):
    if not student_df.empty:
        # Reorder columns for the student DataFrame
        student_columns_order = ["Rank", "StudentID", "StudentName", "Branch", "OfficerType", "Other", "PositionID"]
        student_df = student_df.reindex(columns=student_columns_order)
        
        # Convert StudentID to string to avoid comma formatting
        student_df["StudentID"] = student_df["StudentID"].astype(str)

        st.header("รายงานผลการเลือกตำแหน่ง (ข้อมูลนักเรียน)")
        st.dataframe(student_df, use_container_width=True, hide_index=True)  # Display student data DataFrame without index

    if not position_df.empty:
        # Reorder columns for the position DataFrame
        position_columns_order = ["PositionID", "PositionName", "Unit", "Specialist", "Rank", "Branch", "Other"]
        position_df = position_df.reindex(columns=position_columns_order)

        st.header("รายงานผลการเลือกตำแหน่ง (ข้อมูลตำแหน่ง)")
        st.dataframe(position_df, use_container_width=True, hide_index=True)  # Display position data DataFrame without index

# Streamlit app layout
def main():
    st.title("รายงานผลการเลือกตำแหน่ง")
    
    # Fetch and display data automatically
    student_df, position_df = fetch_data()  # Fetch data and load into DataFrames
    display_data(student_df, position_df)  # Display the data

if __name__ == "__main__":
    main()
