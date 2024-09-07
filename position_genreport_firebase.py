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
            for key, value in data.items():
                # Extract required fields and append them to the list
                student_info = {
                    "Rank": value.get('Rank'),
                    "StudentID": value.get('StudentID'),
                    "RankName": value.get('RankName'),
                    "Branch": value.get('Branch'),
                    "OfficerType": value.get('OfficerType'),
                    "Other": value.get('Other'),
                    "ConfirmedPosition": value.get('ConfirmedPosition', 'Not Confirmed')
                }
                student_data.append(student_info)
            
            # Convert to a DataFrame for sorting
            df = pd.DataFrame(student_data)
            # Sort the DataFrame by 'Rank'
            df.sort_values(by='Rank', inplace=True)
            return df
        else:
            st.warning("No student data found in the database.")
            return pd.DataFrame()  # Return an empty DataFrame if no data
    except Exception as e:
        st.error(f"Error fetching all student data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to render a simple table
def render_simple_table(data):
    """Function to create and display a simple HTML table"""
    html_table = '<table style="width:100%;">'
    html_table += '<tr><th>ลำดับ</th><th>ตำแหน่ง</th><th>สังกัด</th><th>ชกท.</th><th>อัตรา</th><th>เหล่า</th><th>เงื่อนไข</th></tr>'
    for _, row in data.iterrows():
        # Default color is set directly in the row style
        bg_color = 'green' if row.get('ConfirmedPosition', 'Not Confirmed') == 'ว่าง' else 'darkred'
        html_table += f'<tr style="background-color:{bg_color}; color:white;"><td>{row["Rank"]}</td><td>{row["StudentID"]}</td><td>{row["RankName"]}</td><td>{row["Branch"]}</td><td>{row["OfficerType"]}</td><td>{row["Other"]}</td><td>{row["ConfirmedPosition"]}</td></tr>'
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
