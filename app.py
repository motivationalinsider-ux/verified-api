from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import uuid
from datetime import datetime
import qrcode
from PIL import Image
import io
import base64
import os
import requests

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
        created_at TEXT,
        location TEXT,
        commodity TEXT,
        rating REAL,
        deals_completed INTEGER,
        cipc_number TEXT,
        year_founded INTEGER,
        director_name TEXT,
        director_id_verified_date TEXT,
        director_position TEXT,
        contact_person_name TEXT,
        contact_person_title TEXT,
        contact_phone TEXT,
        contact_email TEXT,
        contact_whatsapp TEXT,
        contact_website TEXT,
        dmre_license_number TEXT,
        dmre_license_status TEXT,
        dmre_license_expiry TEXT,
        storage_capacity TEXT,
        storage_location TEXT,
        photos_count INTEGER,
        cipc_verified_date TEXT,
        trade_history_verified_date TEXT,
        location_verified_date TEXT,
        physical_inspection_date TEXT,
        stock_verified_date TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS rfq_responses (
        id TEXT PRIMARY KEY,
        rfq_id TEXT,
        supplier_id TEXT,
        supplier_name TEXT,
        offer_price TEXT,
        offer_quantity TEXT,
        offer_delivery TEXT,
        offer_notes TEXT,
        status TEXT,
        created_at TEXT
    )''')
    
    conn.commit()
    conn.close()

init_db()
print("Database ready!")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========== CAPTCHA VERIFICATION ==========

def verify_captcha(token):
    secret_key = '0x4AAAAAADhbtuxDmFKnFeA3B3s4vIYB4Qc'
    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={'secret': secret_key, 'response': token},
            timeout=5
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"CAPTCHA error: {e}")
        return False

# ========== QR CODE GENERATION ==========

def generate_qr_with_logo(data, logo_path=None):
    if logo_path is None:
        logo_path = os.path.join(os.path.dirname(__file__), 'images', 'QRCODEICON.png')
    
    qr = qrcode.QRCode(version=5, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    try:
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.25)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            pos_x = (qr_width - logo_size) // 2
            pos_y = (qr_height - logo_size) // 2
            
            if logo.mode == 'RGBA':
                qr_img.paste(logo, (pos_x, pos_y), logo)
            else:
                qr_img.paste(logo, (pos_x, pos_y))
    except Exception as e:
        print(f"Logo error: {e}")
    
    return qr_img

@app.route('/api/generate-qr/<user_id>', methods=['GET'])
def generate_qr(user_id):
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT company_name, is_verified FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user[1] != 'verified':
        return jsonify({"error": "User not verified yet"}), 400
    
    # LIVE URL - works on any phone
    qr_data = f"https://verifiedafrica.netlify.app/supplier-profile.html?id={user_id}&from=qr"
    qr_img = generate_qr_with_logo(qr_data)
    
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({"qr_code": img_base64, "qr_url": qr_data})

# ========== USER ENDPOINTS ==========

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = hash_password(data.get('password'))
    full_name = data.get('full_name')
    company_name = data.get('company_name')
    role = data.get('role')
    captcha_token = data.get('cf-turnstile-response')
    
    if not verify_captcha(captcha_token):
        return jsonify({"success": False, "message": "Security check failed"}), 400
    
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
    captcha_token = data.get('cf-turnstile-response')
    
    if not verify_captcha(captcha_token):
        return jsonify({"success": False, "message": "Security check failed"}), 400
    
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
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    columns = ['id', 'email', 'password', 'full_name', 'company_name', 'role', 'is_verified', 'created_at',
               'location', 'commodity', 'rating', 'deals_completed', 'cipc_number', 'year_founded',
               'director_name', 'director_id_verified_date', 'director_position', 'contact_person_name',
               'contact_person_title', 'contact_phone', 'contact_email', 'contact_whatsapp', 'contact_website',
               'dmre_license_number', 'dmre_license_status', 'dmre_license_expiry', 'storage_capacity',
               'storage_location', 'photos_count', 'cipc_verified_date', 'trade_history_verified_date',
               'location_verified_date', 'physical_inspection_date', 'stock_verified_date']
    
    result = {}
    for i, col in enumerate(columns):
        result[col] = user[i]
    
    return jsonify(result)

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT id, company_name, email, full_name, location, commodity, rating, deals_completed, is_verified FROM users WHERE role = 'supplier'")
    suppliers = c.fetchall()
    conn.close()
    return jsonify({"suppliers": [{"id": s[0], "company_name": s[1], "email": s[2], "contact_name": s[3], "location": s[4], "commodity": s[5], "rating": s[6], "deals": s[7], "is_verified": s[8]} for s in suppliers]})

@app.route('/api/user/<user_id>/update', methods=['PUT'])
def update_user(user_id):
    data = request.json
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    
    updates = []
    values = []
    
    allowed_fields = ['director_position', 'contact_person_name', 'contact_person_title', 
                      'contact_phone', 'contact_email', 'contact_whatsapp', 'contact_website',
                      'storage_capacity', 'storage_location']
    
    for field in allowed_fields:
        if field in data and data[field] is not None:
            updates.append(f"{field} = ?")
            values.append(data[field])
    
    if not updates:
        conn.close()
        return jsonify({"success": False, "message": "No fields to update"}), 400
    
    values.append(user_id)
    c.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Profile updated"})

# ========== RFQ ENDPOINTS ==========

rfqs = [
    {
        "id": "1",
        "buyer_name": "ABC Smelters",
        "commodity": "chrome",
        "commodity_display": "Chrome Ore",
        "quantity": "500 MT",
        "location": "sa",
        "location_display": "South Africa",
        "description": "Looking for high-grade chrome ore (42%+ Cr2O3). FOB Musina.",
        "created_at": "2025-06-04"
    },
    {
        "id": "2",
        "buyer_name": "Gauteng Fuel Buyers",
        "commodity": "fuel",
        "commodity_display": "Diesel",
        "quantity": "50,000 L",
        "location": "sa",
        "location_display": "South Africa",
        "description": "Bulk diesel 50ppm. Delivery to Johannesburg.",
        "created_at": "2025-06-03"
    },
    {
        "id": "3",
        "buyer_name": "Harare Milling Company",
        "commodity": "maize",
        "commodity_display": "Maize",
        "quantity": "1000 MT",
        "location": "zim",
        "location_display": "Zimbabwe",
        "description": "White maize for milling. Looking for competitive pricing.",
        "created_at": "2025-06-02"
    }
]

@app.route('/api/rfqs', methods=['GET'])
def get_rfqs():
    return jsonify({"rfqs": rfqs})

@app.route('/api/rfq', methods=['POST'])
def create_rfq():
    data = request.json
    captcha_token = data.get('cf-turnstile-response')
    
    if not verify_captcha(captcha_token):
        return jsonify({"success": False, "message": "Security check failed"}), 400
    
    new_rfq = {
        "id": str(len(rfqs) + 1),
        "buyer_name": data.get('buyer_name'),
        "commodity": data.get('commodity'),
        "commodity_display": data.get('commodity_display'),
        "quantity": data.get('quantity'),
        "location": data.get('location'),
        "location_display": data.get('location_display'),
        "description": data.get('description', ''),
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    rfqs.append(new_rfq)
    return jsonify({"success": True, "rfq": new_rfq})

@app.route('/api/rfq/<rfq_id>/respond', methods=['POST'])
def respond_to_rfq(rfq_id):
    data = request.json
    supplier_id = data.get('supplier_id')
    supplier_name = data.get('supplier_name')
    offer_price = data.get('offer_price')
    offer_quantity = data.get('offer_quantity')
    offer_delivery = data.get('offer_delivery')
    offer_notes = data.get('offer_notes')
    
    response_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("""INSERT INTO rfq_responses 
        (id, rfq_id, supplier_id, supplier_name, offer_price, offer_quantity, offer_delivery, offer_notes, status, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (response_id, rfq_id, supplier_id, supplier_name, offer_price, offer_quantity, offer_delivery, offer_notes, 'pending', created_at))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Response sent to buyer"})

@app.route('/api/rfq/<rfq_id>/responses', methods=['GET'])
def get_rfq_responses(rfq_id):
    conn = sqlite3.connect('verified.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rfq_responses WHERE rfq_id = ? ORDER BY created_at DESC", (rfq_id,))
    responses = c.fetchall()
    conn.close()
    
    return jsonify({"responses": [{"id": r[0], "supplier_name": r[3], "offer_price": r[4], "offer_quantity": r[5], "offer_delivery": r[6], "offer_notes": r[7], "status": r[8], "created_at": r[9]} for r in responses]})

@app.route('/api/blacklist', methods=['GET'])
def get_blacklist():
    return jsonify({"blacklist": [
        {"company": "Global Fuel Trading", "reason": "Fake CIPC certificate", "date": "2025-05-15"},
        {"company": "Chrome Holdings Intl", "reason": "Director ID mismatch", "date": "2025-05-10"},
        {"company": "Beira Commodities Ltd", "reason": "No physical stock", "date": "2025-05-01"}
    ]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)