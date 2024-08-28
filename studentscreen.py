import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import time
import random

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1

# Layout ของแอพ Streamlit
st.title("Live Positions")

# ใช้ st.empty() เพื่อแสดงผลข้อมูลในช่องว่างที่สามารถอัปเดตได้
placeholder = st.empty()

def get_indicator(status):
    """ฟังก์ชันเพื่อคืนค่าสีตามสถานะ"""
    if status == "ว่าง":
        return '<span style="color:green">🟢</span>'
    else:
        return '<span style="color:red">🔴</span>'

def fetch_data_with_retry(sheet, max_retries=3, delay=2):
    """ฟังก์ชันในการดึงข้อมูลด้วยการ retry เมื่อเกิดข้อผิดพลาด"""
    retries = 0
    while retries < max_retries:
        try:
            return pd.DataFrame(sheet.get_all_records())
        except gspread.exceptions.APIError:
            retries += 1
            time.sleep(delay + random.uniform(0, 1))  # เพิ่มเวลาหน่วงแบบสุ่มเพื่อลดโอกาสในการชนกันของการเรียก API
    st.error("ไม่สามารถดึงข้อมูลจาก Google Sheets ได้ในขณะนี้ กรุณาลองใหม่ภายหลัง")
    st.stop()

while True:
    # ดึงข้อมูลจาก Google Sheets
    df_positions = fetch_data_with_retry(position_sheet)

    # การจัดเรียงข้อมูลตามที่ต้องการ
    df_positions = df_positions[['PositionID', 'PositionName', 'Unit', 'Specialist', 'Rank', 'Branch', 'Other', 'Status']]

    # เพิ่มคอลัมน์ Indicator
    df_positions['Indicator'] = df_positions['Status'].apply(get_indicator)

    # รีเซ็ต index ของ DataFrame เพื่อให้เอาคอลัมน์แรกออก
    df_positions.reset_index(drop=True, inplace=True)

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
                cell_content = f"<b>{cell['PositionID']}</b><br>{cell['PositionName']}<br>{cell['Indicator']}"
                html_table += f'<td style="border: 1px solid black; padding: 10px;">{cell_content}</td>'
            else:
                html_table += '<td></td>'  # Empty cell if no data
        html_table += '</tr>'
        rows += 1
    html_table += '</table>'

    # ใช้ placeholder เพื่อแสดงข้อมูลใหม่ในทุกการรีเฟรช
    with placeholder.container():
        st.write("### สถานะตำแหน่ง")
        st.write(html_table, unsafe_allow_html=True)

    time.sleep(30)
