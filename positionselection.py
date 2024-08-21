import gspread
import pandas as pd
import streamlit as st

# Authenticate using gspread with public sheets
gc = gspread.public()

# Open your Google Sheets by URL
sheet_students = gc.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/edit?usp=drive_link').sheet1
sheet_positions = gc.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/edit?usp=drive_link').sheet1

# Convert to pandas DataFrames
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

    # Since this is a local operation, you would need to implement saving back to Google Sheets or update the DataFrame only.

    st.success(f"Position {selected_position_id} assigned to student {selected_student_id}")

# Display the updated positions
if st.button("Refresh Positions Data"):
    st.dataframe(positions_df)
