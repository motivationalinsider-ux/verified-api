import sqlite3
import hashlib
import uuid
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('verified.db')
c = conn.cursor()

# Add verified supplier
suppliers = [
    ("verified@supplier.com", "verified123", "John Verified", "Premium Chrome Trading", "supplier", "verified"),
    ("verified2@supplier.com", "verified123", "Sarah Williams", "Durban Fuel Distributors", "supplier", "verified"),
    ("verified3@supplier.com", "verified123", "Mike Johnson", "Cape Town Agri", "supplier", "verified")
]

for email, pwd, name, company, role, status in suppliers:
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if not c.fetchone():
        user_id = str(uuid.uuid4())
        c.execute("INSERT INTO users (id, email, password, full_name, company_name, role, is_verified, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (user_id, email, hash_password(pwd), name, company, role, status, datetime.now().isoformat()))
        print(f"Added: {email} / {pwd} ({status})")
    else:
        print(f"Already exists: {email}")

conn.commit()
conn.close()
print("Done!")