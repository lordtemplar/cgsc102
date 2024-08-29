import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

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

def get_bg_color(status):
    """ฟังก์ชันเพื่อคืนค่าสีพื้นหลังตามสถานะ"""
    if status == "ว่าง":
        return "green"
    else:
        return "red"

def render_simple_table():
    """ฟังก์ชันในการสร้างและแสดงผลตารางแบบง่าย"""
    html_table = '<table style="width:100%;">'
    html_table += '<tr><th>PositionID</th><th>PositionName</th></tr>'
    for _, row in df_positions.iterrows():
        bg_color = get_bg_color(row['Status'])
        html_table += f'<tr style="background-color:{bg_color}; color:white;"><td>{row["PositionID"]}</td><td>{row["PositionName"]}</td></tr>'
    html_table += '</table>'

    # แสดงผลตาราง
    st.write(html_table, unsafe_allow_html=True)

# เรียกฟังก์ชัน render_simple_table เพื่อแสดงผลตาราง
render_simple_table()
