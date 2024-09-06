import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# โหลด Credential จาก Secrets
firebase_config = {
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase"]["universe_domain"]
}

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://positionchoosing-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# ฟังก์ชันการอ่านข้อมูลจาก Firebase
def get_data():
    ref = db.reference('/')
    data = ref.get()
    return data

# ฟังก์ชันการเขียนข้อมูลไปยัง Firebase
def write_data(path, data):
    ref = db.reference(path)
    ref.set(data)

# การเรียกใช้งานใน Streamlit
st.write('Reading data from Firebase:')
data = get_data()
st.write(data)

st.write('Writing data to Firebase:')
write_data('/example_path', {'name': 'John Doe', 'age': 30})
st.write('Data written!')
