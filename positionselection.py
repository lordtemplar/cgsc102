import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# Set up the Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)
client = gspread.authorize(creds)

# Fetch data from the Google Sheets
sheet_students = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/edit?usp=drive_link').sheet1
sheet_positions = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/edit?usp=drive_link').sheet1

# Convert the data to pandas DataFrames
students_df = pd.DataFrame(sheet_students.get_all_records())
positions_df = pd.DataFrame(sheet_positions.get_all_records())

# Streamlit UI
st.title("Army Staff Officer Position Selection System")

# Display Students and Positions Data
if st.checkbox("Show Students Data"):
    st.dataframe(students_df)

if st.checkbox("Show Positions Data"):
    st.dataframe(positions_df)

# Example function: Select a student and assign a position
st.header("Assign Position to Student")

selected_student_id = st.selectbox("Select Student ID", students_df['StudentID'])
selected_position_id = st.selectbox("Select Position ID", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])

if st.button("Assign Position"):
    # Find the selected student and position
    student_index = students_df[students_df['StudentID'] == selected_student_id].index[0]
    position_index = positions_df[positions_df['PositionID'] == selected_position_id].index[0]

    # Assign the position
    positions_df.at[position_index, 'Status'] = 'ไม่ว่าง'
    positions_df.at[position_index, 'SelectedByStudentID'] = selected_student_id

    # Update the Google Sheet
    sheet_positions.update_cell(position_index + 2, 6, 'ไม่ว่าง')  # Status
    sheet_positions.update_cell(position_index + 2, 7, selected_student_id)  # SelectedByStudentID

    st.success(f"Position {selected_position_id} assigned to student {selected_student_id}")

# Display the updated positions
if st.button("Refresh Positions Data"):
    positions_df = pd.DataFrame(sheet_positions.get_all_records())
    st.dataframe(positions_df)
