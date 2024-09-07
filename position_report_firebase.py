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

# Function to create a DataFrame of data to be updated
def prepare_update_dataframe(student_df, position_df):
    # Check if 'PositionID' column exists in student_df
    if 'PositionID' not in student_df.columns:
        st.error("ไม่พบคอลัมน์ 'PositionID' ในข้อมูลนักเรียนที่ดึงมา กรุณาตรวจสอบฐานข้อมูล.")
        return pd.DataFrame()  # Return empty DataFrame to prevent further errors

    update_data = []
    if not student_df.empty and not position_df.empty:
        for index, student in student_df.iterrows():
            try:
                # Convert PositionID to PositionID-1 format
                position_id_key = str(int(student['PositionID']) - 1)
                if position_id_key in position_df.index:
                    position_info = position_df.loc[position_id_key]
                    update_data.append({
                        'StudentID': student.get('StudentID', 'N/A'),
                        'PositionID': student['PositionID'],
                        'Current PositionName': student.get('PositionName', 'N/A'),
                        'New PositionName': position_info.get('PositionName', 'N/A'),
                        'Current BranchLimit': student.get('BranchLimit', 'N/A'),
                        'New BranchLimit': position_info.get('Branch', 'N/A'),
                        'Current Other': student.get('Other', 'N/A'),
                        'New Other': position_info.get('Other', 'N/A'),
                        'Current PositionRank': student.get('PositionRank', 'N/A'),
                        'New PositionRank': position_info.get('Rank', 'N/A'),
                        'Current Specialist': student.get('Specialist', 'N/A'),
                        'New Specialist': position_info.get('Specialist', 'N/A'),
                        'Current Unit': student.get('Unit', 'N/A'),
                        'New Unit': position_info.get('Unit', 'N/A')
                    })
            except KeyError as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
                continue

    # Convert to DataFrame for display
    update_df = pd.DataFrame(update_data)
    return update_df

# Function to update confirm-student-db with data from internal-position-db
def update_confirm_student_db(position_df):
    try:
        # Fetch current data from confirm-student-db
        student_data_ref = db.reference('/', app=app1)
        student_data = student_data_ref.get()

        # Display spinner while updating
        with st.spinner("กำลังอัปเดตข้อมูล..."):
            # Check if the fetched data is a list or dictionary
            if isinstance(student_data, list):
                # Iterate over student data list
                for i, student in enumerate(student_data):
                    position_id = student.get('PositionID')
                    position_id_key = str(int(position_id) - 1)  # Convert to PositionID-1 format
                    if position_id and position_id_key in position_df.index:
                        # Find the corresponding position data using PositionID-1
                        position_info = position_df.loc[position_id_key]

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
                    position_id_key = str(int(position_id) - 1)  # Convert to PositionID-1 format
                    if position_id and position_id_key in position_df.index:
                        # Find the corresponding position data using PositionID-1
                        position_info = position_df.loc[position_id_key]

                        # Update fields in confirm-student-db
                        student_data_ref.child(key).update({
                            'PositionName': position_info['PositionName'],
                            'BranchLimit': position_info['Branch'],
                            'Other': position_info['Other'],
                            'PositionRank': position_info['Rank'],
                            'Specialist': position_info['Specialist'],
                            'Unit': position_info['Unit']
                        })
        st.success("การอัปเดตข้อมูลเสร็จสมบูรณ์!")
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

    # Prepare the DataFrame to show what will be updated
    update_df = prepare_update_dataframe(student_df, position_df)
    if not update_df.empty:
        st.header("ข้อมูลที่เตรียมสำหรับการอัปเดต")
        st.dataframe(update_df)  # Display what will be updated

    # Update confirm-student-db with data from internal-position-db
    update_confirm_student_db(position_df)

    # Fetch updated data after updating to confirm changes
    student_df, position_df = fetch_data()

    # Display the updated data
    display_data(student_df, position_df)

if __name__ == "__main__":
    main()
