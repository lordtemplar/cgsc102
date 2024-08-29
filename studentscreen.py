import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import time

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets และดึงข้อมูลครั้งเดียว
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1
df_positions = pd.DataFrame(position_sheet.get_all_records())

# ปรับ ID เป็นเลข 3 ตำแหน่ง
df_positions['PositionID'] = df_positions['PositionID'].apply(lambda x: f"{int(x):03d}")

# Layout ของแอพ Streamlit
st.title("Live Positions")

# ใช้ st.empty() เพื่อแสดงผลข้อมูลในช่องว่างที่สามารถอัปเดตได้
placeholder = st.empty()

def get_bg_color_and_text_color(status):
    """ฟังก์ชันเพื่อคืนค่าสีพื้นหลังและสีข้อความตามสถานะ"""
    if status == "ว่าง":
        return "background-color:green; color:white;"  # พื้นหลังสีเขียวและข้อความสีขาว
    else:
        return "background-color:red; color:white;"  # พื้นหลังสีแดงและข้อความสีขาว

def render_table():
    """ฟังก์ชันในการสร้างและแสดงผลตาราง"""
    # สร้าง HTML สำหรับตาราง
    html_table = '<table style="width:100%;">'
    rows = 0
    for i in range(0, len(df_positions), 9):  # 9 columns
        if rows >= 20:  # Limit to 20 rows
            break
        html_table += '<tr>'
        for j in range(9):  # 9 columns
            if i + j < len(df_positions):
                cell = df_positions.iloc[i + j]
                cell_style = get_bg_color_and_text_color(cell['Status'])
                cell_content = f"<div style='{cell_style} padding: 10px; border-radius: 5px;'><b>{cell['PositionID']}</b><br>{cell['PositionName']}</div>"
                html_table += f'<td style="border: 1px solid black;">{cell_content}</td>'
            else:
                html_table += '<td></td>'  # Empty cell if no data
        html_table += '</tr>'
        rows += 1
    html_table += '</table>'

    # ใช้ placeholder เพื่อแสดงข้อมูลใหม่ในทุกการรีเฟรช
    with placeholder.container():
        st.write("### สถานะตำแหน่ง")
        st.write(html_table, unsafe_allow_html=True)

# เรียกฟังก์ชัน render_table เพื่อแสดงผลตาราง
render_table()
