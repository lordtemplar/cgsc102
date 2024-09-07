import streamlit as st
from firebase_admin import db
from firebase_connection import initialize_firebase

# Set the title of the Streamlit app
st.set_page_config(page_title="Position Choose")

# Initialize Firebase connections
app1, app2 = initialize_firebase()

# Function to fetch student data by rank from the first Firebase database
def fetch_student_by_rank(rank):
    try:
        ref = db.reference('/', app=app1)
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'Rank' in value and str(value['Rank']) == str(rank):
                    return key, value  # Return both the key and the student data
        return None, None
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
        return None, None

# Function to update student data in the first Firebase database
def update_student_data(student_key, update_data):
    try:
        ref = db.reference(f"/{student_key}", app=app1)
        ref.update(update_data)
    except Exception as e:
        st.error(f"Error updating student data: {e}")

# Function to fetch position data from the second Firebase database
def fetch_position_data(position_ids):
    try:
        ref = db.reference('/', app=app2)
        data = ref.get()
        matching_positions = {}

        # Check if data is a list or dictionary and process accordingly
        if isinstance(data, dict):
            for key, value in data.items():
                if 'PositionID' in value and int(value['PositionID']) in position_ids:
                    matching_positions[int(value['PositionID'])] = value['PositionName']
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'PositionID' in item and int(item['PositionID']) in position_ids:
                    matching_positions[int(item['PositionID'])] = item['PositionName']

        return matching_positions

    except Exception as e:
        st.error(f"Error fetching position data: {e}")
        return {}

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
        "Name": student_data.get('Name'),
        "Selected Positions": {pos_id: positions.get(pos_id, 'Unknown') for pos_id in selected_positions}
    }

    # Display the merged report
    st.write("## Merged Report")
    st.json(report_data)

# Layout of the Streamlit app
st.title("ระบบเลือกที่ลง CGSC102")

# Input field for rank
rank = st.number_input("Enter Rank to generate report:", min_value=1)

# Button to generate the report
if st.button("Generate Report"):
    generate_report(rank)
