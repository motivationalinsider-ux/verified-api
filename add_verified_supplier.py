import sqlite3
import hashlib
import uuid
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('verified.db')
c = conn.cursor()

# Full verified supplier data
suppliers = [
    {
        "email": "verified@supplier.com",
        "password": "verified123",
        "full_name": "Johannes van der Merwe",
        "company_name": "Premium Chrome Trading",
        "role": "supplier",
        "is_verified": "verified",
        "location": "Musina, South Africa",
        "commodity": "Chrome Ore (42%+ Cr2O3)",
        "rating": 4.8,
        "deals_completed": 47,
        "cipc_number": "2024/123456/07",
        "year_founded": 2020,
        "director_name": "Johannes van der Merwe",
        "director_id_verified_date": "2025-06-01",
        "director_position": "Managing Director",
        "contact_person_name": "Pieter Botha",
        "contact_person_title": "Sales Manager",
        "contact_phone": "+27 82 456 7890",
        "contact_email": "pieter@premiumchrome.co.za",
        "contact_whatsapp": "082 456 7890",
        "contact_website": "www.premiumchrome.co.za",
        "cipc_verified_date": "2025-06-01",
        "trade_history_verified_date": "2025-06-05",
        "location_verified_date": "2025-06-10",
        "physical_inspection_date": "2025-06-15",
        "stock_verified_date": "2025-06-01",
        "photos_count": 4
    },
    {
        "email": "verified2@supplier.com",
        "password": "verified123",
        "full_name": "Michael Naidoo",
        "company_name": "Durban Fuel Distributors",
        "role": "supplier",
        "is_verified": "verified",
        "location": "Durban, South Africa",
        "commodity": "Diesel (50ppm, 500ppm)",
        "rating": 4.9,
        "deals_completed": 156,
        "cipc_number": "2019/567890/07",
        "year_founded": 2019,
        "director_name": "Michael Naidoo",
        "director_id_verified_date": "2025-05-10",
        "director_position": "Managing Director",
        "contact_person_name": "Thabo Mkhize",
        "contact_person_title": "Wholesale Manager",
        "contact_phone": "+27 11 345 6789",
        "contact_email": "thabo@durbanfuel.co.za",
        "contact_whatsapp": "083 456 7890",
        "contact_website": "www.durbanfuel.co.za",
        "dmre_license_number": "DMRE/WL/2024/12345",
        "dmre_license_status": "Active",
        "dmre_license_expiry": "2026-12-31",
        "storage_capacity": "2,500,000 litres",
        "storage_location": "Durban Depot",
        "cipc_verified_date": "2025-05-10",
        "trade_history_verified_date": "2025-05-15",
        "location_verified_date": "2025-05-20",
        "physical_inspection_date": "2025-06-01",
        "stock_verified_date": "2025-06-01",
        "photos_count": 8
    },
    {
        "email": "verified3@supplier.com",
        "password": "verified123",
        "full_name": "Sarah Williams",
        "company_name": "Cape Town Agri",
        "role": "supplier",
        "is_verified": "verified",
        "location": "Cape Town, South Africa",
        "commodity": "Soyameal, Maize, Wheat",
        "rating": 4.7,
        "deals_completed": 112,
        "cipc_number": "2018/12345/07",
        "year_founded": 2018,
        "director_name": "Sarah Williams",
        "director_id_verified_date": "2025-04-15",
        "director_position": "CEO",
        "contact_person_name": "John Peters",
        "contact_person_title": "Export Manager",
        "contact_phone": "+27 21 345 6789",
        "contact_email": "john@capetownagri.co.za",
        "contact_whatsapp": "082 345 6789",
        "contact_website": "www.capetownagri.co.za",
        "cipc_verified_date": "2025-04-15",
        "trade_history_verified_date": "2025-04-20",
        "location_verified_date": "2025-04-25",
        "stock_verified_date": "2025-05-15",
        "photos_count": 5
    }
]

for s in suppliers:
    c.execute("SELECT * FROM users WHERE email = ?", (s["email"],))
    if not c.fetchone():
        user_id = str(uuid.uuid4())
        c.execute("""INSERT INTO users (
            id, email, password, full_name, company_name, role, is_verified, created_at,
            location, commodity, rating, deals_completed, cipc_number, year_founded,
            director_name, director_id_verified_date, director_position,
            contact_person_name, contact_person_title, contact_phone, contact_email,
            contact_whatsapp, contact_website, dmre_license_number, dmre_license_status,
            dmre_license_expiry, storage_capacity, storage_location, photos_count,
            cipc_verified_date, trade_history_verified_date, location_verified_date,
            physical_inspection_date, stock_verified_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, s["email"], hash_password(s["password"]), s["full_name"], s["company_name"], s["role"], s["is_verified"], datetime.now().isoformat(),
         s.get("location"), s.get("commodity"), s.get("rating"), s.get("deals_completed"), s.get("cipc_number"), s.get("year_founded"),
         s.get("director_name"), s.get("director_id_verified_date"), s.get("director_position"),
         s.get("contact_person_name"), s.get("contact_person_title"), s.get("contact_phone"), s.get("contact_email"),
         s.get("contact_whatsapp"), s.get("contact_website"), s.get("dmre_license_number"), s.get("dmre_license_status"),
         s.get("dmre_license_expiry"), s.get("storage_capacity"), s.get("storage_location"), s.get("photos_count"),
         s.get("cipc_verified_date"), s.get("trade_history_verified_date"), s.get("location_verified_date"),
         s.get("physical_inspection_date"), s.get("stock_verified_date")))
        print(f"Added: {s['email']}")
    else:
        print(f"Already exists: {s['email']}")

conn.commit()
conn.close()
print("\n✅ Verified suppliers added with full data!")