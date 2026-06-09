import sqlite3

conn = sqlite3.connect('verified.db')
c = conn.cursor()

# Complete data for verified@supplier.com
c.execute("""
    UPDATE users SET 
        company_name = 'Premium Chrome Trading',
        cipc_number = '2024/123456/07',
        year_founded = 2020,
        location = 'Musina, South Africa',
        commodity = 'Chrome Ore (42%+ Cr2O3)',
        rating = 4.8,
        deals_completed = 47,
        director_name = 'Johannes van der Merwe',
        director_id_verified_date = '2025-06-01',
        director_position = 'Managing Director',
        contact_person_name = 'Pieter Botha',
        contact_person_title = 'Sales Manager',
        contact_phone = '+27 82 456 7890',
        contact_email = 'pieter@premiumchrome.co.za',
        contact_whatsapp = '082 456 7890',
        contact_website = 'www.premiumchrome.co.za',
        cipc_verified_date = '2025-06-01',
        trade_history_verified_date = '2025-06-05',
        location_verified_date = '2025-06-10',
        physical_inspection_date = '2025-06-15',
        stock_verified_date = '2025-06-01',
        photos_count = 4,
        is_verified = 'verified'
    WHERE email = 'verified@supplier.com'
""")

print(f"Updated {c.rowcount} row(s) for verified@supplier.com")

# Also update verified@buyer.com
c.execute("""
    UPDATE users SET 
        company_name = 'Premium Buyers International',
        location = 'Cape Town, South Africa',
        commodity = 'Chrome Ore, Fuel, Agriculture',
        rating = 4.5,
        deals_completed = 23,
        contact_person_name = 'Sarah Williams',
        contact_person_title = 'Procurement Manager',
        contact_phone = '+27 21 345 6789',
        contact_email = 'sarah@premiumbuyers.co.za',
        is_verified = 'verified'
    WHERE email = 'verified@buyer.com'
""")

print(f"Updated {c.rowcount} row(s) for verified@buyer.com")

conn.commit()
conn.close()
print("\n✅ Supplier and buyer data updated successfully!")