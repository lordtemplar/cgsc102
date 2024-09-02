import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import pandas as pd
import time

# ตั้งค่า Firebase Admin SDK
try:
    # ตรวจสอบว่ามีการตั้งค่าแล้วหรือยัง เพื่อหลีกเลี่ยงการ initialize ซ้ำ
    firebase_admin.get_app()
except ValueError:
    # ระบุ path ไปยังไฟล์ JSON ของ Service Account Key
    cred = credentials.Certificate("positionchoosing-firebase-adminsdk-vr2az-04309817a7.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'  # URL ของ Firebase Realtime Database
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
    # ดึงข้อมูลจาก Firebase Realtime Database
    ref = db.reference('positions')  # เปลี่ยน 'positions' เป็นชื่อของโหนดในฐานข้อมูล Firebase ของคุณ
    data = ref.get()

    # ตรวจสอบว่ามีข้อมูลหรือไม่
    if data:
        # สร้าง DataFrame จากข้อมูลที่ดึงมา
        df_positions = pd.DataFrame(data.values())
    else:
        st.error("ไม่พบข้อมูลใน Firebase Realtime Database")
        return

    # ปรับ ID เป็นเลข 3 ตำแหน่ง
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
