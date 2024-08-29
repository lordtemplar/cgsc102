import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import time

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# ฟังก์ชันเพื่อคืนค่าสีพื้นหลังและสีข้อความตามสถานะ
def get_bg_color_and_text_color(status):
    if status == "ว่าง":
        return "background-color:green; color:white;"  # พื้นหลังสีเขียวและข้อความสีขาว
    else:
        return "background-color:red; color:white;"  # พื้นหลังสีแดงและข้อความสีขาว

# Layout ของแอพ Streamlit
st.title("Live Positions")

# ใช้ st.empty() เพื่อแสดงผลข้อมูลในช่องว่างที่สามารถอัปเดตได้
placeholder = st.empty()

while True:
    # ดึงข้อมูลจาก Google Sheets
    position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1
    df_positions = pd.DataFrame(position_sheet.get_all_records())

    # การจัดเรียงข้อมูลตามที่ต้องการ
    df_positions = df_positions[['PositionID', 'PositionName', 'Unit', 'Specialist', 'Rank', 'Branch', 'Other', 'Status']]

    # ปรับ ID เป็นเลข 3 ตำแหน่ง
    df_positions['PositionID'] = df_positions['PositionID'].apply(lambda x: f"{int(x):03d}")

    # สร้าง HTML สำหรับบล็อคข้อมูลที่ปรับตามขนาดหน้าจอ
    html_blocks = '<div style="display: flex; flex-wrap: wrap; gap: 10px; overflow-y: auto; max-height: 90vh;">'

    for index, row in df_positions.iterrows():
        cell_style = get_bg_color_and_text_color(row['Status'])
        block_content = f"""
        <div style='{cell_style} padding: 15px; border-radius: 5px; width: 200px; text-align: center;'>
            <b>{row['PositionID']}</b><br>{row['PositionName']}
        </div>
        """
        html_blocks += block_content

    html_blocks += '</div>'

    # แสดงผล HTML ใน Streamlit
    with placeholder.container():
        st.components.v1.html(html_blocks, height=800, scrolling=True)

    # หน่วงเวลา 1 นาที (60 วินาที) ก่อนอัปเดตข้อมูลใหม่
    time.sleep(60)
