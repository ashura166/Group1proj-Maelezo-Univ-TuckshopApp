import firebase_admin
from firebase_admin import credentials, firestore

# Check if the default app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(r"C:\Users\asha\Maelezo Uni Tuckshop\ServiceAccountKey.json")
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()


# Firestore client
db = firestore.client()
