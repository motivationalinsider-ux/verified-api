import sqlite3
import hashlib
import uuid
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('verified.db')
c = conn.cursor()

# Test accounts
test_accounts = [
    {
        "email": "verified@supplier.com",
        "password": "verified123",
        "full_name": "Verified Supplier",
        "company_name": "Verified Trading Co",
        "role": "supplier",
        "is_verified": "verified",
        "location": "Johannesburg, South Africa",
        "commodity": "Chrome Ore, Diesel",
        "rating": 4.8,
        "deals_completed": 47
    },
    {
        "email": "verified@buyer.com",
        "password": "verified123",
        "full_name": "Verified Buyer",
        "company_name": "Verified Buyers Ltd",
        "role": "buyer",
        "is_verified": "verified",
        "location": "Cape Town, South Africa",
        "commodity": "Chrome, Fuel, Agriculture"
    },
    {
        "email": "browser@test.com",
        "password": "browser123",
        "full_name": "Test Browser",
        "company_name": "Research Co",
        "role": "browser",
        "is_verified": "pending"
    },
    {
        "email": "broker@test.com",
        "password": "broker123",
        "full_name": "Test Broker",
        "company_name": "Global Trade Brokers",
        "role": "broker",
        "is_verified": "pending"
    }
]

for acc in test_accounts:
    # Check if already exists
    c.execute("SELECT * FROM users WHERE email = ?", (acc["email"],))
    if not c.fetchone():
        user_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        c.execute("""INSERT INTO users (
            id, email, password, full_name, company_name, role, is_verified, created_at,
            location, commodity, rating, deals_completed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, acc["email"], hash_password(acc["password"]), acc["full_name"], 
         acc["company_name"], acc["role"], acc["is_verified"], created_at,
         acc.get("location"), acc.get("commodity"), acc.get("rating"), acc.get("deals_completed")))
        print(f"Added: {acc['email']} ({acc['role']})")
    else:
        print(f"Already exists: {acc['email']}")

conn.commit()
conn.close()
print("\n✅ Test accounts added!")