import pandas as pd
import streamlit as st

# URLs for your Google Sheets
positions_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/export?format=csv'
students_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/export?format=csv'

# Read the data into pandas DataFrames
positions_df = pd.read_csv(positions_url)
students_df = pd.read_csv(students_url)

# Debugging: Check the column names
st.write("Positions DataFrame Columns:", positions_df.columns.tolist())
st.write("Students DataFrame Columns:", students_df.columns.tolist())

# Streamlit UI
st.title("Army Staff Officer Position Selection System")

# Navigation Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Show Information", "Edit Student Information", "Assign Position", "Edit Assigned Position"])

# Section 1: Show Information
if section == "Show Information":
    st.header("Show Information")
    st.subheader("Student Information")
    st.dataframe(students_df)

    st.subheader("Position Information")
    st.dataframe(positions_df)

# Section 2: Edit Student Information
elif section == "Edit Student Information":
    st.header("Edit Student Information")
    
    student_id = st.selectbox("Select Student ID to Edit", students_df['StudentID'])
    student_data = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    # Debugging: Check the student_data content
    st.write("Selected Student Data:", student_data)
    
    # Make sure 'Score' exists in student_data
    if 'Score' in student_data:
        score = st.number_input("Score", value=student_data['Score'], step=1)
    else:
        st.error("Score column is missing in the student data!")
        score = st.number_input("Score", step=1)
    
    rank_name = st.text_input("Rank Name", student_data['RankName'])
    branch = st.selectbox("Branch", ["ร.", "ม.", "ป."], index=["ร.", "ม.", "ป."].index(student_data['Branch']))
    officer_type = st.selectbox("Officer Type", ["นร.", "นป.", "ปริญญา", "พิเศษ"], index=["นร.", "นป.", "ปริญญา", "พิเศษ"].index(student_data['OfficerType']))
    
    if st.button("Update Student Information"):
        students_df.loc[students_df['StudentID'] == student_id, ['RankName', 'Branch', 'OfficerType', 'Score']] = [rank_name, branch, officer_type, score]
        st.success("Student information updated!")

# The rest of the sections (Assign Position, Edit Assigned Position) would follow...
