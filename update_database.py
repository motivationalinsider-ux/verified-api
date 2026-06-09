import sqlite3

conn = sqlite3.connect('verified.db')
c = conn.cursor()

# Add all missing columns to users table
try:
    c.execute("ALTER TABLE users ADD COLUMN location TEXT")
    print("Added: location")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN commodity TEXT")
    print("Added: commodity")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN rating REAL")
    print("Added: rating")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN deals_completed INTEGER DEFAULT 0")
    print("Added: deals_completed")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN cipc_number TEXT")
    print("Added: cipc_number")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN year_founded INTEGER")
    print("Added: year_founded")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN director_name TEXT")
    print("Added: director_name")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN director_id_verified_date TEXT")
    print("Added: director_id_verified_date")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN director_position TEXT")
    print("Added: director_position")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN contact_person_name TEXT")
    print("Added: contact_person_name")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN contact_person_title TEXT")
    print("Added: contact_person_title")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN contact_phone TEXT")
    print("Added: contact_phone")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN contact_email TEXT")
    print("Added: contact_email")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN contact_whatsapp TEXT")
    print("Added: contact_whatsapp")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN contact_website TEXT")
    print("Added: contact_website")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN dmre_license_number TEXT")
    print("Added: dmre_license_number")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN dmre_license_status TEXT")
    print("Added: dmre_license_status")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN dmre_license_expiry TEXT")
    print("Added: dmre_license_expiry")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN storage_capacity TEXT")
    print("Added: storage_capacity")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN storage_location TEXT")
    print("Added: storage_location")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN photos_count INTEGER DEFAULT 0")
    print("Added: photos_count")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN cipc_verified_date TEXT")
    print("Added: cipc_verified_date")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN trade_history_verified_date TEXT")
    print("Added: trade_history_verified_date")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN location_verified_date TEXT")
    print("Added: location_verified_date")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN physical_inspection_date TEXT")
    print("Added: physical_inspection_date")
except: pass

try:
    c.execute("ALTER TABLE users ADD COLUMN stock_verified_date TEXT")
    print("Added: stock_verified_date")
except: pass

conn.commit()
conn.close()
print("\n✅ Database updated successfully!")