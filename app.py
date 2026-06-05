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
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS verifications (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        cipc_file TEXT,
        director_name TEXT,
        director_id TEXT,
        status TEXT,
        submitted_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        reporter_name TEXT,
        reporter_email TEXT,
        reported_company TEXT,
        reason TEXT,
        details TEXT,
        status TEXT,
        submitted_at TEXT
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
        c.execute("INSERT INTO users (id, email, password, full_name, company_name, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (user_id, email, password, full_name, company_name, role, created_at))
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
    c.execute("SELECT id, email, full_name, company_name, role FROM users WHERE email = ? AND password = ?", (email, password))
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
                "role": user[4]
            }
        })
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, email, full_name, company_name, role FROM users")
    users = c.fetchall()
    conn.close()
    return jsonify({"users": [{"id": u[0], "email": u[1], "name": u[2], "company": u[3], "role": u[4]} for u in users]})

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, email, full_name, company_name, role, created_at FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "id": user[0],
            "email": user[1],
            "full_name": user[2],
            "company_name": user[3],
            "role": user[4],
            "created_at": user[5]
        })
    else:
        return jsonify({"error": "User not found"}), 404

# ========== SUPPLIER ENDPOINTS ==========

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, company_name, email, full_name FROM users WHERE role = 'supplier'")
    suppliers = c.fetchall()
    conn.close()
    return jsonify({"suppliers": [{"id": s[0], "company_name": s[1], "email": s[2], "contact_name": s[3]} for s in suppliers]})

# ========== VERIFICATION ENDPOINTS ==========

@app.route('/api/verify/submit', methods=['POST'])
def submit_verification():
    data = request.json
    user_id = data.get('user_id')
    cipc_file = data.get('cipc_file', '')
    director_name = data.get('director_name')
    director_id = data.get('director_id')
    
    verification_id = str(uuid.uuid4())
    submitted_at = datetime.now().isoformat()
    
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("INSERT INTO verifications (id, user_id, cipc_file, director_name, director_id, status, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (verification_id, user_id, cipc_file, director_name, director_id, 'pending', submitted_at))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Verification submitted. We'll review within 48 hours."})

# ========== REPORT ENDPOINTS ==========

@app.route('/api/report/submit', methods=['POST'])
def submit_report():
    data = request.json
    reporter_name = data.get('reporter_name', '')
    reporter_email = data.get('reporter_email')
    reported_company = data.get('reported_company')
    reason = data.get('reason')
    details = data.get('details', '')
    
    report_id = str(uuid.uuid4())
    submitted_at = datetime.now().isoformat()
    
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("INSERT INTO reports (id, reporter_name, reporter_email, reported_company, reason, details, status, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (report_id, reporter_name, reporter_email, reported_company, reason, details, 'pending', submitted_at))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Report submitted. We'll investigate."})

@app.route('/api/blacklist', methods=['GET'])
def get_blacklist():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT reported_company, reason, status, submitted_at FROM reports WHERE status = 'confirmed'")
    reports = c.fetchall()
    conn.close()
    return jsonify({"blacklist": [{"company": r[0], "reason": r[1], "status": r[2], "date": r[3]} for r in reports]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)