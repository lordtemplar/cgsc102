import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("Starting the script...")

# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('boreal-dock-433205-b0-87525a85b092.json', scope)
print("Credentials loaded...")

client = gspread.authorize(creds)
print("Client authorized...")

# Open the Google Sheet
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lwfcVb8GwSLN9RSZyiyzaCjS8jywgaNS5Oj8k7Lhemw').sheet1
print("Google Sheet opened...")

# Read and print all data from the sheet
data = sheet.get_all_records()
print("Data read from sheet...")

print(data)
