from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        company_name TEXT,
        role TEXT,
        is_verified TEXT,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS rfqs (
        id TEXT PRIMARY KEY,
        buyer_id TEXT,
        buyer_name TEXT,
        commodity TEXT,
        commodity_display TEXT,
        quantity TEXT,
        location TEXT,
        location_display TEXT,
        description TEXT,
        timeline TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

init_db()
print("Database ready!")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========== USER ENDPOINTS ==========

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = hash_password(data.get('password'))
    full_name = data.get('full_name')
    company_name = data.get('company_name')
    role = data.get('role')
    
    user_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (id, email, password, full_name, company_name, role, is_verified, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (user_id, email, password, full_name, company_name, role, 'pending', created_at))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User created", "user_id": user_id})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = hash_password(data.get('password'))
    
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, email, full_name, company_name, role, is_verified FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "success": True,
            "user": {
                "id": user[0],
                "email": user[1],
                "full_name": user[2],
                "company_name": user[3],
                "role": user[4],
                "is_verified": user[5]
            }
        })
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, email, full_name, company_name, role, is_verified FROM users")
    users = c.fetchall()
    conn.close()
    return jsonify({"users": [{"id": u[0], "email": u[1], "name": u[2], "company": u[3], "role": u[4], "is_verified": u[5]} for u in users]})

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, email, full_name, company_name, role, is_verified, created_at FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "id": user[0],
            "email": user[1],
            "full_name": user[2],
            "company_name": user[3],
            "role": user[4],
            "is_verified": user[5],
            "created_at": user[6]
        })
    else:
        return jsonify({"error": "User not found"}), 404

# ========== SUPPLIER ENDPOINTS ==========

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, company_name, email, full_name, is_verified FROM users WHERE role = 'supplier'")
    suppliers = c.fetchall()
    conn.close()
    return jsonify({"suppliers": [{"id": s[0], "company_name": s[1], "email": s[2], "contact_name": s[3], "is_verified": s[4]} for s in suppliers]})

# ========== RFQ ENDPOINTS ==========

# Initial dummy RFQs
dummy_rfqs = [
    {"id": "1", "buyer_name": "ABC Smelters", "commodity": "chrome", "commodity_display": "Chrome Ore", "quantity": "500 MT", "location": "sa", "location_display": "South Africa", "description": "Looking for high-grade chrome ore (42%+ Cr2O3)", "timeline": "30 days", "created_at": "2025-06-04"},
    {"id": "2", "buyer_name": "Gauteng Fuel", "commodity": "fuel", "commodity_display": "Diesel", "quantity": "50,000 L", "location": "sa", "location_display": "South Africa", "description": "Bulk diesel 50ppm", "timeline": "ASAP", "created_at": "2025-06-03"},
    {"id": "3", "buyer_name": "Harare Milling", "commodity": "maize", "commodity_display": "Maize", "quantity": "1000 MT", "location": "zim", "location_display": "Zimbabwe", "description": "White maize for milling", "timeline": "45 days", "created_at": "2025-06-02"}
]

@app.route('/api/rfqs', methods=['GET'])
def get_rfqs():
    return jsonify({"rfqs": dummy_rfqs})

@app.route('/api/rfq', methods=['POST'])
def create_rfq():
    data = request.json
    new_rfq = {
        "id": str(len(dummy_rfqs) + 1),
        "buyer_name": data.get('buyer_name'),
        "commodity": data.get('commodity'),
        "commodity_display": data.get('commodity_display'),
        "quantity": data.get('quantity'),
        "location": data.get('location'),
        "location_display": data.get('location_display'),
        "description": data.get('description', ''),
        "timeline": data.get('timeline', 'Negotiable'),
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    dummy_rfqs.append(new_rfq)
    return jsonify({"success": True, "rfq": new_rfq})

# ========== REPORT ENDPOINTS ==========

@app.route('/api/blacklist', methods=['GET'])
def get_blacklist():
    return jsonify({"blacklist": [
        {"company": "Global Fuel Trading", "reason": "Fake CIPC certificate", "date": "2025-05-15"},
        {"company": "Chrome Holdings Intl", "reason": "Director ID mismatch", "date": "2025-05-10"}
    ]})

@app.route('/api/report/submit', methods=['POST'])
def submit_report():
    data = request.json
    return jsonify({"success": True, "message": "Report submitted. We'll investigate."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)