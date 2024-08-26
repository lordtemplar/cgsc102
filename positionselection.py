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
        # Placeholder to update the table in place
        table_placeholder = st.empty()
        table_placeholder.write(student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)

        # Display Edit and Next buttons
        col1, col2, _ = st.columns([1, 1, 3])
        
        with col1:
            edit_clicked = st.button("Edit", key="edit_button")
        
        with col2:
            next_clicked = st.button("Next", key="next_button")
        
        # Handle Edit button click
        if edit_clicked or "edit_mode" in st.session_state:
            st.session_state.edit_mode = True

            # Preserve input field values in session state
            if "rank_name" not in st.session_state:
                st.session_state.rank_name = student_data.iloc[0]['RankName']
            if "branch" not in st.session_state:
                st.session_state.branch = student_data.iloc[0]['Branch']
            if "officer_type" not in st.session_state:
                st.session_state.officer_type = student_data.iloc[0]['OfficerType']
            if "other" not in st.session_state:
                st.session_state.other = student_data.iloc[0]['Other']

            st.write("### Edit Student Information")
            st.session_state.rank_name = st.text_input("Rank Name", st.session_state.rank_name)
            st.session_state.branch = st.text_input("Branch", st.session_state.branch)
            st.session_state.officer_type = st.text_input("Officer Type", st.session_state.officer_type)
            st.session_state.other = st.text_input("Other", st.session_state.other)

            # Update button
            if st.button("Update Information", key="update_button"):
                updated_data = [
                    student_id, 
                    st.session_state.rank_name, 
                    st.session_state.branch, 
                    st.session_state.officer_type, 
                    st.session_state.other
                ]
                
                # Find the row number in the Google Sheet
                cell = student_sheet.find(student_id)
                if cell:
                    row_number = cell.row
                    
                    # Update the Google Sheet row (only update the columns we are interested in)
                    try:
                        student_sheet.update(f'A{row_number}:E{row_number}', [updated_data])
                        st.success(f"Successfully updated Student ID {student_id}.")
                        
                        # Reload and update the same table with the refreshed data
                        df_students = pd.DataFrame(student_sheet.get_all_records())
                        df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()
                        updated_student_data = df_students[df_students['StudentID'] == student_id.strip()]
                        
                        # Refresh the existing table with the updated data
                        table_placeholder.write(updated_student_data[['StudentID', 'RankName', 'Branch', 'OfficerType', 'Other']].to_html(index=False), unsafe_allow_html=True)

                        # Clear the edit mode
                        st.session_state.clear()
                    except Exception as e:
                        st.error(f"Failed to update: {e}")
                else:
                    st.error("Student ID not found in Google Sheet.")
    else:
        st.error("Student ID not found.")
