import pandas as pd
import streamlit as st

# URLs for your Google Sheets
positions_url = 'https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ/export?format=csv'
students_url = 'https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw/export?format=csv'

# Read the data into pandas DataFrames
positions_df = pd.read_csv(positions_url)
students_df = pd.read_csv(students_url)

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
    
    rank_name = st.text_input("Rank Name", student_data['RankName'])
    branch = st.selectbox("Branch", ["ร.", "ม.", "ป."], index=["ร.", "ม.", "ป."].index(student_data['Branch']))
    officer_type = st.selectbox("Officer Type", ["นร.", "นป.", "ปริญญา", "พิเศษ"], index=["นร.", "นป.", "ปริญญา", "พิเศษ"].index(student_data['OfficerType']))
    score = st.number_input("Score", value=student_data['Score'], step=1)
    
    if st.button("Update Student Information"):
        students_df.loc[students_df['StudentID'] == student_id, ['RankName', 'Branch', 'OfficerType', 'Score']] = [rank_name, branch, officer_type, score]
        st.success("Student information updated!")

# Section 3: Assign Position
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
        st.success(f"Positions assigned to student {student_id}")

# Section 4: Edit Assigned Position
elif section == "Edit Assigned Position":
    st.header("Edit Assigned Position")
    
    student_id = st.selectbox("Select Student ID to Edit Assigned Position", students_df['StudentID'])
    selected_student = students_df[students_df['StudentID'] == student_id].iloc[0]
    
    position1 = st.selectbox("1st Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position1']].index[0])
    position2 = st.selectbox("2nd Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position2']].index[0])
    position3 = st.selectbox("3rd Choice", positions_df['PositionID'], index=positions_df[positions_df['PositionID'] == selected_student['Position3']].index[0])
    
    if st.button("Update Assigned Positions"):
        # Update positions based on the student ID
        students_df.loc[students_df['StudentID'] == student_id, ['Position1', 'Position2', 'Position3']] = [position1, position2, position3]
        st.success(f"Assigned positions updated for student {student_id}")

# Optional: Refresh the data if needed
if st.sidebar.button("Refresh Data"):
    positions_df = pd.read_csv(positions_url)
    students_df = pd.read_csv(students_url)
    st.experimental_rerun()
