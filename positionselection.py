import pandas as pd
import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# URLs for your Google Sheets (CSV format)
positions_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/export?format=csv'
students_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/export?format=csv'

# Read the data into pandas DataFrames
positions_df = pd.read_csv(positions_url, dtype={'PositionID': str, 'SelectedByStudentID': str})
students_df = pd.read_csv(students_url, dtype={'StudentID': str})

# Replace any NaN values in SelectedByStudentID and Other columns with "ไม่มี"
positions_df['SelectedByStudentID'] = positions_df['SelectedByStudentID'].fillna("ไม่มี")
students_df['Other'] = students_df['Other'].fillna("ไม่มี")

# Streamlit UI
st.title("Army Staff Officer Position Selection System")

# Navigation Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Student Information", "Position Information", "Edit Student Information", "Assign Position", "Edit Assigned Position"])

# Section 1: Student Information
if section == "Student Information":
    st.header("Student Information")
    student_id = st.text_input("Enter Student ID")
    
    if st.button("Search"):
        if student_id:
            student_data = students_df[students_df['StudentID'] == student_id]
            if not student_data.empty:
                st.table(student_data.set_index('StudentID'))
            else:
                st.warning("Student ID not found.")
        else:
            st.warning("Please enter a Student ID.")
    
    if st.button("Show All"):
        st.table(students_df.set_index('StudentID'))

# Section 2: Position Information
elif section == "Position Information":
    st.header("Position Information")
    position_id = st.text_input("Enter Position ID")
    
    if st.button("Search"):
        if position_id:
            position_data = positions_df[positions_df['PositionID'] == position_id]
            if not position_data.empty:
                st.table(position_data.set_index('PositionID'))
            else:
                st.warning("Position ID not found.")
        else:
            st.warning("Please enter a Position ID.")
    
    if st.button("Show All"):
        st.table(positions_df.set_index('PositionID'))

# Section 3: Edit Student Information
elif section == "Edit Student Information":
    st.header("Edit Student Information")
    
    student_id = st.text_input("Enter Student ID to Edit")
    
    if st.button("Search Student"):
        student_data = students_df[students_df['StudentID'] == student_id]
        if not student_data.empty:
            # Debugging output to verify columns
            st.write("Available columns in student_data:", student_data.columns.tolist())
            
            # Display fields for editing
            student_record = student_data.iloc[0]  # Get the first row as a Series
            
            # Safely access columns using .get() to avoid KeyError
            rank_name = st.text_input("Rank Name", student_record.get('RankName', ''))
            branch_options = ["ร.", "ม.", "ป."]
            current_branch = student_record.get('Branch', 'ร.')
            if current_branch not in branch_options:
                current_branch = 'ร.'  # Default value if current_branch not in options
            branch = st.selectbox("Branch", branch_options, index=branch_options.index(current_branch))
            
            officer_type_options = ["นร.", "นป.", "ปริญญา", "พิเศษ"]
            current_officer_type = student_record.get('OfficerType', 'นร.')
            if current_officer_type not in officer_type_options:
                current_officer_type = 'นร.'  # Default value if current_officer_type not in options
            officer_type = st.selectbox("Officer Type", officer_type_options, index=officer_type_options.index(current_officer_type))
            
            # Replace 'Score' with 'Rank'
            rank = st.text_input("Rank", value=student_record.get('Rank', ''))
            
            other = st.text_input("Other", value=student_record.get('Other', 'ไม่มี'))
            
            if st.button("Update"):
                # Update the DataFrame
                students_df.loc[students_df['StudentID'] == student_id, ['RankName', 'Branch', 'OfficerType', 'Rank', 'Other']] = [rank_name, branch, officer_type, rank, other]
                
                # Update the Google Sheet
                # Since the sheet is publicly editable, we'll assume we can overwrite it via a CSV upload method.
                # However, Google Sheets doesn't support direct CSV uploads via HTTP POST requests.
                # Instead, consider using the Google Sheets API with proper authentication.
                
                # For demonstration, here's how you might update the sheet using gspread with credentials:
                try:
                    # Define the scope and credentials
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)
                    client = gspread.authorize(creds)
                    
                    # Open the Google Sheet
                    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1
                    
                    # Find the row number where StudentID matches
                    cell = sheet.find(student_id)
                    if cell:
                        row = cell.row
                        # Update the row with new data
                        # Assuming columns: A: StudentID, B: RankName, C: Branch, D: OfficerType, E: Rank, F: Other
                        sheet.update_cell(row, 2, rank_name)
                        sheet.update_cell(row, 3, branch)
                        sheet.update_cell(row, 4, officer_type)
                        sheet.update_cell(row, 5, rank)
                        sheet.update_cell(row, 6, other)
                        
                        st.success("Student information updated successfully in Google Sheets!")
                    else:
                        st.error("Student ID not found in Google Sheets.")
                except Exception as e:
                    st.error(f"An error occurred while updating Google Sheets: {e}")
        else:
            st.warning("Student ID not found.")

# Section 4: Assign Position
elif section == "Assign Position":
    st.header("Assign Position to Student")

    student_id = st.selectbox("Select Student ID", students_df['StudentID'])
    selected_student = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    available_positions = positions_df[positions_df['Status'] == 'ว่าง']['PositionID'].tolist()
    position1 = st.selectbox("1st Choice", available_positions)
    position2 = st.selectbox("2nd Choice", available_positions)
    position3 = st.selectbox("3rd Choice", available_positions)
    
    if st.button("Assign Positions"):
        students_df.loc[students_df['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
        positions_df.loc[positions_df['PositionID'].isin([position1, position2, position3]), 'Status'] = 'ไม่ว่าง'
        positions_df.loc[positions_df['PositionID'].isin([position1, position2, position3]), 'SelectedByStudentID'] = student_id
        
        st.success(f"Positions assigned to student {student_id}")

# Section 5: Edit Assigned Position
elif section == "Edit Assigned Position":
    st.header("Edit Assigned Position")
    
    student_id = st.selectbox("Select Student ID to Edit Assigned Position", students_df['StudentID'])
    selected_student = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    position1 = st.selectbox("1st Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position1']].index[0] if selected_student['Position1'] in positions_df['PositionID'].values else 0)
    position2 = st.selectbox("2nd Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position2']].index[0] if selected_student['Position2'] in positions_df['PositionID'].values else 0)
    position3 = st.selectbox("3rd Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position3']].index[0] if selected_student['Position3'] in positions_df['PositionID'].values else 0)
    
    if st.button("Update Assigned Positions"):
        students_df.loc[students_df['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
        positions_df.loc[positions_df['PositionID'].isin([position1, position2, position3]), 'SelectedByStudentID'] = student_id
        st.success(f"Assigned positions updated for student {student_id}")

# Optional: Refresh the data if needed
if st.sidebar.button("Refresh Data"):
    positions_df = pd.read_csv(positions_url, dtype={'PositionID': str, 'SelectedByStudentID': str})
    students_df = pd.read_csv(students_url, dtype={'StudentID': str})
    positions_df['SelectedByStudentID'] = positions_df['SelectedByStudentID'].fillna("ไม่มี")
    students_df['Other'] = students_df['Other'].fillna("ไม่มี")
    st.experimental_rerun()
