import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import time

# ตั้งค่าข้อมูลรับรองของ Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets
position_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mflUv6jyOqTXplPGiSxCOp7wJ1HHd4lQ4BSIzvuBgoQ').sheet1

# ฟังก์ชันในการดึงข้อมูลและแสดงผลตาราง
def load_and_display_data():
    # ดึงข้อมูลจาก Google Sheets
    df_positions = pd.DataFrame(position_sheet.get_all_records())

    # แสดงตารางข้อมูล
    st.write("### สถานะตำแหน่ง")
    st.table(df_positions[['PositionID', 'PositionName', 'Unit', 'Status']])

# Layout ของแอพ Streamlit
st.title("สถานะตำแหน่ง - CGSC102")

# เรียกฟังก์ชันแสดงผลข้อมูล
load_and_display_data()

# ตั้งเวลาให้หน้ารีเฟรชทุก 5 วินาที
time.sleep(5)
st.experimental_rerun()

