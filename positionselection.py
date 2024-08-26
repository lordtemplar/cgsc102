import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

st.title("Google Sheets Connection Test")

# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
client = gspread.authorize(creds)

st.write("Credentials loaded and client authorized...")

# Open the Google Sheet
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1

st.write("Google Sheet opened...")

# Read and display all data from the sheet
data = sheet.get_all_records()
st.write("Data read from sheet:")
st.write(data)
