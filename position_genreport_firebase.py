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

# Function to generate the report by merging data from both databases
def generate_report(rank):
    # Fetch student data by rank
    student_key, student_data = fetch_student_by_rank(rank)
    if not student_data:
        st.warning(f"No student found with rank {rank}.")
        return

    # Extract the position IDs selected by the student
    selected_positions = student_data.get('SelectedPositions', [])  # Assume it is a list of IDs

    if not selected_positions:
        st.warning(f"No positions selected by the student with rank {rank}.")
        return

    # Fetch position data for the selected positions
    positions = fetch_position_data(selected_positions)

    # Merge student data and positions into a single report
    report_data = {
        "StudentID": student_data.get('StudentID'),
        "Rank": student_data.get('Rank'),
        "Name": student_data.get('RankName'),
        "Selected Positions": {pos_id: positions.get(pos_id, 'Unknown') for pos_id in selected_positions}
    }

    # Display the merged report
    st.write("## Merged Report")
    st.json(report_data)

# Layout of the Streamlit app
st.title("ระบบเลือกที่ลง CGSC102")

# Display the table with all student information sorted by rank
st.write("### Student Information")
students_df = fetch_all_students()
if not students_df.empty:
    st.dataframe(students_df)

# Input field for rank
rank = st.number_input("Enter Rank to generate report:", min_value=1)

# Button to generate the report
if st.button("Generate Report"):
    generate_report(rank)
