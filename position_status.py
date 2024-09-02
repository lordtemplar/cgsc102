import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

# ฟังก์ชันสำหรับการตรวจสอบและเชื่อมต่อ Firebase Admin SDK
def initialize_firebase_app():
    try:
        # ตรวจสอบว่า Firebase Admin SDK ถูกตั้งค่าแล้วหรือยัง
        if not firebase_admin._apps:
            st.write("Initializing Firebase...")
            # ใช้ไฟล์ JSON ของ Service Account Key ที่อยู่ในโฟลเดอร์เดียวกัน
            cred = credentials.Certificate("positionchoosing-firebase-adminsdk-vr2az-a74f69f4eb.json")  # ใช้ชื่อไฟล์ JSON ที่คุณมี
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'  # ใช้ URL ของ Firebase ที่คุณให้มา
            })
            st.write("Firebase initialized successfully.")
        else:
            st.write("Firebase already initialized.")
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        st.stop()

# ฟังก์ชันทดสอบการดึงข้อมูลจาก Firebase Realtime Database
def fetch_data_from_firebase():
    try:
        st.write("Attempting to fetch data from Firebase Realtime Database...")
        # ดึงข้อมูลจาก Firebase Realtime Database
        ref = db.reference("alert_logs")  # ใช้ชื่อโหนด (node) ที่ต้องการดึงข้อมูล
        data = ref.get()
        if data:
            st.write("Data fetched successfully.")
            st.write(data)  # แสดงข้อมูลที่ดึงมาเพื่อทดสอบ
        else:
            st.write("No data found.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# เรียกใช้ฟังก์ชัน
if __name__ == "__main__":
    st.set_page_config(page_title="Firebase Test")
    st.title("Firebase Connection Test")

    initialize_firebase_app()  # เรียกใช้ฟังก์ชันเพื่อเชื่อมต่อ Firebase
    fetch_data_from_firebase()  # ทดสอบการดึงข้อมูลจาก Firebase
