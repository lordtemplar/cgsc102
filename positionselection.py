import pandas as pd
import streamlit as st
import requests

# URLs for your Google Sheets (CSV format)
positions_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/export?format=csv'
students_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/export?format=csv'

# Read the data into pandas DataFrames
positions_df = pd.read_csv(positions_url, dtype={'PositionID': str, 'SelectedByStudentID': str})
students_df = pd.read_csv(students_url, dtype={'StudentID': str})

# Replace any NaN values in SelectedByStudentID and Other columns with "ไม่มี"
positions_df['SelectedByStudentID'] = positions_df['SelectedByStudentID'].fillna("ไม่มี")
students_df['Other'] = students_df['Other'].fillna("import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw') # Replace with your Google Sheets URL
worksheet = sheet.sheet1  # or replace with the name of your sheet

# Function to load data into a DataFrame
def load_data():
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    return df

# Function to update a specific row in the Google Sheet
def update_row(student_id, updated_data):
    cell = worksheet.find(student_id)
    if cell:
        row = cell.row
        worksheet.update(f'B{row}:F{row}', [updated_data])  # Update columns B to F
        return True
    return False

# Function to filter positions based on student data
def filter_positions(df_positions, branch, officer_type, other_condition):
    filtered_positions = df_positions[(df_positions['BranchCondition'] == branch) &
                                      (df_positions['OfficerTypeCondition'] == officer_type) &
                                      (df_positions['OtherCondition'] == other_condition)]
    return filtered_positions

# Step 1: Input Student ID
st.title("Student Position Selection System")
student_id = st.text_input("Enter Student ID:")

if student_id:
    # Step 2: Show Student Information with "EDIT" and "NEXT" buttons
    df_students = load_data()
    student_data = df_students[df_students['StudentID'] == student_id]
    
    if not student_data.empty:
        st.write("### Student Information")
        st.table(student_data)
        
        if st.button("EDIT"):
            # Step 3: Edit mode
            st.write("### Edit Student Information")
            rank_name = st.text_input("Rank Name", student_data.iloc[0]['RankName'])
            branch = st.selectbox("Branch", ["ร.", "ม.", "ป."], index=["ร.", "ม.", "ป."].index(student_data.iloc[0]['Branch']))
            officer_type = st.selectbox("Officer Type", ["นร.", "นป.", "ปริญญา", "พิเศษ"], index=["นร.", "นป.", "ปริญญา", "พิเศษ"].index(student_data.iloc[0]['OfficerType']))
            rank = st.text_input("Rank", student_data.iloc[0]['Rank'])
            other = st.text_input("Other", student_data.iloc[0]['Other'])
            
            if st.button("SAVE"):
                if update_row(student_id, [rank_name, branch, officer_type, rank, other]):
                    st.success("Student information updated successfully!")
                else:
                    st.error("Failed to update student information.")
        
        if st.button("NEXT"):
            # Step 4: Position Selection Step
            df_positions = pd.read_csv('positions.csv')  # Assume positions data is loaded from a CSV file
            st.write("### Position Selection")
            
            # Filter positions based on the student's branch, officer type, and other condition
            filtered_positions = filter_positions(df_positions, student_data.iloc[0]['Branch'], 
                                                  student_data.iloc[0]['OfficerType'], 
                                                  student_data.iloc[0]['Other'])
            
            if not filtered_positions.empty:
                st.write("#### Available Positions")
                st.table(filtered_positions)
                
                position1 = st.selectbox("1st Choice", filtered_positions['PositionID'].tolist())
                position2 = st.selectbox("2nd Choice", filtered_positions['PositionID'].tolist())
                position3 = st.selectbox("3rd Choice", filtered_positions['PositionID'].tolist())
                
                if st.button("SUBMIT"):
                    # Save the selected positions
                    df_students.loc[df_students['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
                    st.write("### Review Selected Positions")
                    st.table(df_students[df_students['StudentID'] == student_id][['StudentID', 'RankName', 'Branch', 'OfficerType', 'Position1', 'Position2', 'Position3']])
                    
                    if st.button("CONFIRM"):
                        # Update Google Sheets with selected positions
                        if update_row(student_id, [rank_name, branch, officer_type, rank, other]):
                            st.success("Student positions confirmed and saved!")
                        else:
                            st.error("Failed to save positions.")
            else:
                st.warning("No positions available that match your criteria.")
    else:
        st.error("Student ID not found.")
ม่มี")

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
            with st.form(key="edit_student_form"):
                student_record = student_data.iloc[0]  # Get the first row as a Series
                
                # Display editable fields
                rank_name = st.text_input("Rank Name", student_record.get('RankName', ''))
                branch = st.selectbox("Branch", ["ร.", "ม.", "ป."], index=["ร.", "ม.", "ป."].index(student_record.get('Branch', 'ร.')))
                officer_type = st.selectbox("Officer Type", ["นร.", "นป.", "ปริญญา", "พิเศษ"], index=["นร.", "นป.", "ปริญญา", "พิเศษ"].index(student_record.get('OfficerType', 'นร.')))
                rank = st.text_input("Rank", value=student_record.get('Rank', ''))
                other = st.text_input("Other", value=student_record.get('Other', 'ไม่มี'))
                
                submitted = st.form_submit_button("Update")
                
                if submitted:
                    # Send the data to the Google Apps Script
                    apps_script_url = "https://script.google.com/macros/s/AKfycbx2G2IrhP3OJONqQxJNbvuYaB3aU45fPR6pC27WPfrFkmRJLNMxshacYRB89HbwXApZIg/exec"
                    data = {
                        "StudentID": student_id,
                        "RankName": rank_name,
                        "Branch": branch,
                        "OfficerType": officer_type,
                        "Rank": rank,
                        "Other": other
                    }
                    response = requests.post(apps_script_url, json=data)
                    
                    if response.status_code == 200:
                        st.success("Student information updated successfully in Google Sheets!")
                    else:
                        st.error("Failed to update Google Sheets. Please check the Apps Script or network connection.")
        else:
            st.warning("Student ID not found.")

# Section 4: Assign Position
elif section == "Assign Position":
    st.header("Assign Position to Student")

    student_id = st.selectbox("Select Student ID", students_df['StudentID'])
    selected_student = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    position1 = st.selectbox("1st Choice", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])
    position2 = st.selectbox("2nd Choice", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])
    position3 = st.selectbox("3rd Choice", positions_df[positions_df['Status'] == 'ว่าง']['PositionID'])
    
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
