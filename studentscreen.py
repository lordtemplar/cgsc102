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

# ฟังก์ชันในการคำนวณจำนวนคอลัมน์ตามขนาดหน้าจอ
def calculate_columns(window_width):
    if window_width < 600:
        return 2
    elif window_width < 900:
        return 3
    elif window_width < 1200:
        return 4
    else:
        return 6  # ปรับจำนวนคอลัมน์ตามความเหมาะสม

# ฟังก์ชันเพื่อคืนค่าสีพื้นหลังและสีข้อความตามสถานะ
def get_bg_color_and_text_color(status):
    if status == "ว่าง":
        return "background-color:green; color:white;"  # พื้นหลังสีเขียวและข้อความสีขาว
    else:
        return "background-color:red; color:white;"  # พื้นหลังสีแดงและข้อความสีขาว

# ฟังก์ชันในการสร้างและแสดงผลตาราง
def render_table(columns):
    # สร้าง HTML สำหรับตาราง
    html_table = '<table style="width:100%;">'
    rows = 0
    for i in range(0, len(df_positions), columns):  # ใช้จำนวนคอลัมน์ที่คำนวณได้
        if rows >= (153 // columns):  # เพิ่มแถวตามจำนวนคอลัมน์เพื่อให้ครบ 153 บล็อก
            break
        html_table += '<tr>'
        for j in range(columns):
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

    st.write("### สถานะตำแหน่ง")
    st.write(html_table, unsafe_allow_html=True)

# ดึงขนาดหน้าต่างของผู้ใช้
window_width = st.slider("ปรับขนาดหน้าต่างเพื่อทดสอบ", min_value=400, max_value=1600, value=800)

# คำนวณจำนวนคอลัมน์ตามขนาดหน้าต่าง
columns = calculate_columns(window_width)

# เรียกฟังก์ชัน render_table เพื่อแสดงผลตาราง
render_table(columns)
