import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# ตรวจสอบว่ามี Secret ที่จำเป็นครบถ้วน
try:
    # ตรวจสอบว่ามีการเรียกใช้ Firebase app แล้วหรือยัง
    if not firebase_admin._apps:
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

        # ใช้ Credential ที่ถูกต้องในการเชื่อมต่อ
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

except ValueError as e:
    st.error(f"Firebase initialization error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

# ฟังก์ชันการอ่านข้อมูลจาก Firebase
def get_data(path='/'):
    ref = db.reference(path)  # เส้นทางไปยังตำแหน่งข้อมูล
    data = ref.get()
    return data

# ดึงข้อมูลจาก Firebase
data = get_data('/')

# ตรวจสอบว่ามีข้อมูลหรือไม่
if data:
    # สร้าง DataFrame จากข้อมูล
    df = pd.DataFrame(data.values())

    # เรียงลำดับคอลัมน์ตามที่ต้องการ
    df = df[["PositionID", "PositionName", "Unit", "Specialist", "Branch", "Rank", "Other", "Status"]]

    # ฟังก์ชันการเปลี่ยนสีพื้นหลังของเซลล์ตามเงื่อนไข
    def highlight_status(status):
        return ['background-color: darkred' if s == 'ไม่ว่าง' else '' for s in status]

    # ใช้ Styler เพื่อเปลี่ยนสีพื้นหลัง
    styled_df = df.style.apply(highlight_status, subset=['Status'])

    # แสดงผลข้อมูลในรูปแบบตารางที่สามารถขยายขนาดได้
    st.write("Data from Firebase:")
    st.dataframe(styled_df, use_container_width=True)
else:
    st.write("No data found in Firebase.")
