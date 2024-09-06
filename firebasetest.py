import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# เริ่มต้นการใช้งาน Firebase Admin SDK ด้วย Credential JSON
cred_path = r'C:\Users\JUTSUMARU\Desktop\FirebaseJSON\positionchoosing-firebase-adminsdk-vr2az-bff93d8f1d.json'
cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# ฟังก์ชันตัวอย่างเพื่ออ่านข้อมูลจาก Firebase Realtime Database
def get_data():
    ref = db.reference('/')
    data = ref.get()
    return data

# ฟังก์ชันตัวอย่างเพื่อเขียนข้อมูลไปยัง Firebase Realtime Database
def write_data(path, data):
    ref = db.reference(path)
    ref.set(data)

# ตัวอย่างการเรียกใช้งานใน Streamlit
st.write('Reading data from Firebase:')
data = get_data()
st.write(data)

st.write('Writing data to Firebase:')
write_data('/example_path', {'name': 'John Doe', 'age': 30})
st.write('Data written!')
