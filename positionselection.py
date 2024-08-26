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
st.title("Student Information Management")

# Step 1: Search Box to Get Student ID
student_id = st.text_input("Enter Student ID:")

if student_id:
    # Load student data
    df_students = pd.DataFrame(student_sheet.get_all_records())
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

    # Find the student data by Student ID
    student_data = df_students[df_students['StudentID'] == student_id.strip()]
    
    if not student_data.empty:
        st.write("### Student Information")
        st.table(student_data)

        # Display Edit and Next buttons
        col1, col2, _ = st.columns([1, 1, 3])
        
        with col1:
            edit_clicked = st.button("Edit")
        
        with col2:
            next_clicked = st.button("Next")
        
        # Handle Edit button click
        if edit_clicked:
            st.write("### Edit Student Information")
            rank_name = st.text_input("Rank Name", student_data.iloc[0]['RankName'])
            branch = st.text_input("Branch", student_data.iloc[0]['Branch'])
            officer_type = st.text_input("Officer Type", student_data.iloc[0]['OfficerType'])
            other = st.text_input("Other", student_data.iloc[0]['Other'])
            rank = st.text_input("Rank", student_data.iloc[0]['Rank'])
            position1 = st.text_input("Position 1", student_data.iloc[0]['Position1'])
            position2 = st.text_input("Position 2", student_data.iloc[0]['Position2'])
            position3 = st.text_input("Position 3", student_data.iloc[0]['Position3'])

            # Update button
            if st.button("Update Information"):
                updated_data = [student_id, rank_name, branch, officer_type, other, rank, position1, position2, position3]
                
                # Find the row number in the Google Sheet
                cell = student_sheet.find(student_id)
                if cell:
                    row_number = cell.row
                    
                    # Update the Google Sheet row
                    try:
                        student_sheet.update(f'A{row_number}:I{row_number}', [updated_data])
                        st.success(f"Successfully updated Student ID {student_id}.")
                        
                        # Reload and display updated data
                        df_students = pd.DataFrame(student_sheet.get_all_records())
                        st.write("### Updated Student Information")
                        st.table(df_students[df_students['StudentID'] == student_id.strip()])
                    except Exception as e:
                        st.error(f"Failed to update: {e}")
                else:
                    st.error("Student ID not found in Google Sheet.")
    else:
        st.error("Student ID not found.")
