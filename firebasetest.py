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

# เริ่มการใช้งาน Firebase
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# ฟังก์ชันเพื่ออ่านข้อมูลจาก Firebase Realtime Database
def get_data():
    ref = db.reference('/')
    data = ref.get()
    return data

# อ่านข้อมูลจาก Firebase
data = get_data()

# ตรวจสอบว่ามีข้อมูลหรือไม่
if data:
    # แปลงข้อมูลให้เป็น DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')

    # แสดงข้อมูลในรูปแบบตารางใน Streamlit
    st.write("ข้อมูลจาก Firebase Realtime Database:")
    st.dataframe(df)
else:
    st.write("ไม่พบข้อมูลใน Firebase Realtime Database.")
