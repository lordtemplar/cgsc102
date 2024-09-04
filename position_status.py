import os
import firebase_admin
from firebase_admin import credentials

# Load the environment variable for the credentials path
service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

try:
    # Check if the Firebase app is already initialized
    if not firebase_admin._apps:
        print("Starting Firebase connection...")

        # Initialize Firebase app with credentials from environment variable
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)

        print("Firebase connection established successfully.")
    else:
        print("Firebase app is already initialized. Using the existing app.")

except Exception as e:
    print(f"An error occurred during Firebase initialization: {e}")
