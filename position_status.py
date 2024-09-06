import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import time

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

# ตั้งค่า Firebase Admin SDK ด้วย Credential ที่โหลดจาก Secrets
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# เปลี่ยน Title บน browser tab
st.set_page_config(page_title="LIVE Position")

# เพิ่มกล่องค้นหาด้านบน (นอกฟังก์ชันและลูปเพื่อป้องกัน Duplicate Widget ID)
if "search_term" not in st.session_state:
    st.session_state.search_term = st.text_input("ค้นหา ลำดับ, ตำแหน่ง, สังกัด, ชกท., อัตรา, เหล่า หรือ เงื่อนไข")

# Layout ของแอพ Streamlit
st.title("Live Positions")

# สร้างพื้นที่ว่างเพื่ออัปเดตข้อมูลตาราง
placeholder = st.empty()

def load_data_and_render_table():
    # อ่านข้อมูลจาก Firebase Realtime Database
    ref = db.reference('/positions')  # สมมุติว่าโหนดที่เก็บข้อมูลตำแหน่งใน Firebase คือ '/positions'
    data = ref.get()

    # แปลงข้อมูลเป็น DataFrame
    df_positions = pd.DataFrame(data)

    # ปรับค่า ID เป็นเลข 3 ตำแหน่ง
    df_positions['PositionID'] = df_positions['PositionID'].apply(lambda x: f"{int(x):03d}")

    def get_bg_color(status):
        """ฟังก์ชันเพื่อคืนค่าสีพื้นหลังตามสถานะ"""
        if status == "ว่าง":
            return "green"
        else:
            return "darkred"

    def render_simple_table(data):
        """ฟังก์ชันในการสร้างและแสดงผลตารางแบบง่าย"""
        html_table = '<table style="width:100%;">'
        html_table += '<tr><th>ลำดับ</th><th>ตำแหน่ง</th><th>สังกัด</th><th>ชกท.</th><th>อัตรา</th><th>เหล่า</th><th>เงื่อนไข</th></tr>'
        for _, row in data.iterrows():
            bg_color = get_bg_color(row['Status'])
            html_table += f'<tr style="background-color:{bg_color}; color:white;"><td>{row["PositionID"]}</td><td>{row["PositionName"]}</td><td>{row["Unit"]}</td><td>{row["Specialist"]}</td><td>{row["Rank"]}</td><td>{row["Branch"]}</td><td>{row["Other"]}</td></tr>'
        html_table += '</table>'

        # แสดงผลตารางในพื้นที่ว่างที่สร้างขึ้น
        placeholder.write(html_table, unsafe_allow_html=True)

    # กรองข้อมูลตามคำค้นหา
    if st.session_state.search_term:
        filtered_positions = df_positions[df_positions.apply(lambda row: st.session_state.search_term.lower() in str(row['PositionID']).lower() or st.session_state.search_term.lower() in row['PositionName'].lower() or st.session_state.search_term.lower() in row['Unit'].lower() or st.session_state.search_term.lower() in row['Specialist'].lower() or st.session_state.search_term.lower() in row['Rank'].lower() or st.session_state.search_term.lower() in row['Branch'].lower() or st.session_state.search_term.lower() in row['Other'].lower(), axis=1)]
    else:
        filtered_positions = df_positions

    # เรียกฟังก์ชัน render_simple_table เพื่อแสดงผลตาราง
    render_simple_table(filtered_positions)

# ใช้ loop เพื่ออัปเดตข้อมูลทุก 1 นาที
while True:
    load_data_and_render_table()
    time.sleep(60)
