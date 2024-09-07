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

# Function to update confirm-student-db with data from internal-position-db
def update_confirm_student_db(position_df):
    try:
        # Fetch current data from confirm-student-db
        student_data_ref = db.reference('/', app=app1)
        student_data = student_data_ref.get()

        # Check if the fetched data is a list or dictionary
        if isinstance(student_data, list):
            # Iterate over student data list
            for i, student in enumerate(student_data):
                position_id = student.get('PositionID')
                if position_id and str(position_id) in position_df.index:
                    # Find the corresponding position data using PositionID
                    position_info = position_df.loc[str(position_id)]

                    # Update fields in confirm-student-db
                    student_data_ref.child(str(i)).update({
                        'PositionName': position_info['PositionName'],
                        'BranchLimit': position_info['Branch'],
                        'Other': position_info['Other'],
                        'PositionRank': position_info['Rank'],
                        'Specialist': position_info['Specialist'],
                        'Unit': position_info['Unit']
                    })

        elif isinstance(student_data, dict):
            # Iterate over student data dictionary
            for key, student in student_data.items():
                position_id = student.get('PositionID')
                if position_id and str(position_id) in position_df.index:
                    # Find the corresponding position data using PositionID
                    position_info = position_df.loc[str(position_id)]

                    # Update fields in confirm-student-db
                    student_data_ref.child(key).update({
                        'PositionName': position_info['PositionName'],
                        'BranchLimit': position_info['Branch'],
                        'Other': position_info['Other'],
                        'PositionRank': position_info['Rank'],
                        'Specialist': position_info['Specialist'],
                        'Unit': position_info['Unit']
                    })

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปเดตฐานข้อมูล: {e}")

# Function to display data from DataFrames
def display_data(student_df, position_df):
    if not student_df.empty:
        st.header("รายงานผลการเลือกตำแหน่ง")
        st.dataframe(student_df)  # Display student data DataFrame

    if not position_df.empty:
        st.header("รายงานผลการเลือกตำแหน่ง (ข้อมูลตำแหน่ง)")
        st.dataframe(position_df)  # Display position data DataFrame

# Streamlit app layout
def main():
    st.title("รายงานผลการเลือกตำแหน่ง")

    # Fetch data from both databases
    student_df, position_df = fetch_data()  

    # Update confirm-student-db with data from internal-position-db
    update_confirm_student_db(position_df)

    # Display the updated data
    display_data(student_df, position_df)

if __name__ == "__main__":
    main()
