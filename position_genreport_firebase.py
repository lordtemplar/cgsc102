from firebase_connection import initialize_firebase
from firebase_admin import db

# Initialize Firebase connections
app1, app2 = initialize_firebase()

def synchronize_databases_by_position_id(position_id):
    """
    Synchronizes data between the two Firebase databases based on PositionID.
    
    Args:
        position_id (str): The PositionID used to identify and synchronize data.
    """
    # Fetch data from the first Firebase database (internal-student-db)
    student_ref = db.reference('/students', app=app1)
    students_data = student_ref.order_by_child('ConfirmedPosition').equal_to(position_id).get()

    # Fetch data from the second Firebase database (internal-position-db)
    position_ref = db.reference(f'/positions/{position_id}', app=app2)
    position_data = position_ref.get()

    # Perform synchronization logic here
    if position_data and position_data.get('Status') == 'ว่าง':
        if students_data:
            # Update the position status to 'ไม่ว่าง' if a student confirmed the position
            position_ref.update({'Status': 'ไม่ว่าง'})
            for student_key, student in students_data.items():
                # Update student information accordingly
                student_ref.child(student_key).update({'PositionStatus': 'ไม่ว่าง'})
            st.write(f"Synchronized data for PositionID {position_id}")

# Example usage
synchronize_databases_by_position_id('001')
