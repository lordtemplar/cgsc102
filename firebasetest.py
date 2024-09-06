import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# โหลด Credential จาก Secrets
firebase_config = {
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase"]["universe_domain"]
}

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# ฟังก์ชันการอ่านข้อมูลจาก Firebase
def get_data():
    ref = db.reference('/')  # ใช้เส้นทางที่เหมาะสม
    data = ref.get()
    return data

# ดึงข้อมูลจาก Firebase
data = get_data()

# ตรวจสอบว่ามีข้อมูลหรือไม่
if data:
    # แปลงข้อมูลเป็น DataFrame
    df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
    
    # แสดงผลข้อมูลในรูปแบบตาราง
    st.write("Data from Firebase:")
    st.dataframe(df)
else:
    st.write("No data found in Firebase.")
