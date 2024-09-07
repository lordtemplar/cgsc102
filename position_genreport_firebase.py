import streamlit as st
from firebase_admin import db
from firebase_connection import initialize_firebase
import pandas as pd

# Set the title of the Streamlit app
st.set_page_config(page_title="Position Choose")

# Initialize Firebase connections
app1, app2 = initialize_firebase()

# Function to fetch all student data from the first Firebase database
def fetch_all_students():
    try:
        ref = db.reference('/', app=app1)
        data = ref.get()
        if data:
            student_data = []
            
            # Check if the data is a list or a dictionary and process accordingly
            if isinstance(data, list):
                # If data is a list, iterate directly over it
                for value in data:
                    if isinstance(value, dict):  # Ensure each item is a dictionary
                        student_info = {
                            "ลำดับ": int(value.get('Rank', 0)),  # Convert to integer to remove decimal
                            "รหัสนักเรียน": value.get('StudentID'),
                            "ยศ ชื่อ สกุล": value.get('RankName'),
                            "เหล่า": value.get('Branch'),
                            "กำเนิด": value.get('OfficerType'),
                            "เงื่อนไข": value.get('Other'),
                            "ตำแหน่งที่เลือก": value.get('ConfirmedPosition', 'Not Confirmed')
                        }
                        student_data.append(student_info)
            elif isinstance(data, dict):
                # If data is a dictionary, iterate using items()
                for key, value in data.items():
                    if isinstance(value, dict):  # Ensure each item is a dictionary
                        student_info = {
                            "ลำดับ": int(value.get('Rank', 0)),  # Convert to integer to remove decimal
                            "รหัสนักเรียน": value.get('StudentID'),
                            "ยศ ชื่อ สกุล": value.get('RankName'),
                            "เหล่า": value.get('Branch'),
                            "กำเนิด": value.get('OfficerType'),
                            "เงื่อนไข": value.get('Other'),
                            "ตำแหน่งที่เลือก": value.get('ConfirmedPosition', 'Not Confirmed')
                        }
                        student_data.append(student_info)
            
            # Convert to a DataFrame for sorting
            if student_data:
                df = pd.DataFrame(student_data)
                # Sort the DataFrame by 'ลำดับ'
                df.sort_values(by='ลำดับ', inplace=True)
                return df
            else:
                st.warning("No valid student data found in the database.")
                return pd.DataFrame()  # Return an empty DataFrame if no valid data
        else:
            st.warning("No student data found in the database.")
            return pd.DataFrame()  # Return an empty DataFrame if no data
    except Exception as e:
        st.error(f"Error fetching all student data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to render a simple table without background colors
def render_simple_table(data):
    """Function to create and display a simple HTML table"""
    html_table = '<table style="width:100%; border-collapse: collapse;">'
    # Header row
    html_table += '<tr><th>ลำดับ</th><th>รหัสนักเรียน</th><th>ยศ ชื่อ สกุล</th><th>เหล่า</th><th>กำเนิด</th><th>เงื่อนไข</th><th>ตำแหน่งที่เลือก</th></tr>'
    for _, row in data.iterrows():
        html_table += f'<tr><td>{row["ลำดับ"]}</td><td>{row["รหัสนักเรียน"]}</td><td>{row["ยศ ชื่อ สกุล"]}</td><td>{row["เหล่า"]}</td><td>{row["กำเนิด"]}</td><td>{row["เงื่อนไข"]}</td><td>{row["ตำแหน่งที่เลือก"]}</td></tr>'
    html_table += '</table>'
    st.markdown(html_table, unsafe_allow_html=True)

# Layout of the Streamlit app
st.title("ระบบเลือกที่ลง CGSC102")

# Fetch and display the table with all student information sorted by rank
students_df = fetch_all_students()
if not students_df.empty:
    render_simple_table(students_df)
else:
    st.write("No data available to display.")
