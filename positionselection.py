import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# Open the updated Google Sheets
student_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1

# Function to load data into a DataFrame
def load_student_data():
    records = student_sheet.get_all_records()
    df = pd.DataFrame(records)
    st.write("Loaded student data:", df)  # Debugging output to check data
    return df

# Function to load position data into a DataFrame
def load_position_data():
    records = position_sheet.get_all_records()
    df = pd.DataFrame(records)
    return df

# Streamlit App Layout
st.title("Student Position Selection System")

# Step 1: Input Student ID
student_id = st.text_input("Enter Student ID:")

if student_id:
    # Load student data
    df_students = load_student_data()

    st.write(f"Searching for Student ID: {student_id}")  # Debugging output to check what we're searching for

    # Ensure that StudentID is treated as a string for comparison
    df_students['StudentID'] = df_students['StudentID'].astype(str)

    student_data = df_students[df_students['StudentID'] == student_id]

    if not student_data.empty:
        st.write("### Student Information")
        st.table(student_data)
    else:
        st.error("Student ID not found.")
