import sqlite3
import hashlib
import uuid
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_dummy_data():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    
    # Dummy users
    dummy_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "demo_supplier@verified.africa",
            "password": hash_password("supplier123"),
            "full_name": "John Smith",
            "company_name": "Musina Chrome Trading",
            "role": "supplier",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "demo_buyer@verified.africa",
            "password": hash_password("buyer123"),
            "full_name": "Sarah Jones",
            "company_name": "Gauteng Smelters",
            "role": "buyer",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "demo_browser@verified.africa",
            "password": hash_password("browser123"),
            "full_name": "Mike Brown",
            "company_name": "Market Research Co",
            "role": "browser",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "demo_broker@verified.africa",
            "password": hash_password("broker123"),
            "full_name": "Lisa Wong",
            "company_name": "Global Trade Brokers",
            "role": "broker",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for user in dummy_users:
        try:
            c.execute("INSERT INTO users (id, email, password, full_name, company_name, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (user["id"], user["email"], user["password"], user["full_name"], user["company_name"], user["role"], user["created_at"]))
            print(f"Added: {user['email']} ({user['role']})")
        except sqlite3.IntegrityError:
            print(f"User already exists: {user['email']}")
    
    conn.commit()
    conn.close()
    print("\n✅ Dummy data added successfully!")

if __name__ == '__main__':
    add_dummy_data()