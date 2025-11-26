"""Query the database to verify data persistence."""
import sqlite3

conn = sqlite3.connect('gym_edge.db')
cursor = conn.cursor()

# Get all tables
print("=== DATABASE TABLES ===")
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\n=== DEVICES ===")
devices = cursor.execute('SELECT * FROM devices').fetchall()
for dev in devices:
    print(f"  ID: {dev[0]}, Device: {dev[1]}, API Key: {dev[2]}")

print("\n=== MEMBERS ===")
members = cursor.execute('SELECT id, name, nfc_uid, membership_status, membership_expiry FROM members').fetchall()
for m in members:
    print(f"  ID: {m[0]}, Name: {m[1]}, NFC: {m[2]}, Status: {m[3]}, Expiry: {m[4]}")

print("\n=== CHECK-INS (Recent 5) ===")
checkins = cursor.execute('SELECT id, member_id, check_in_time, check_out_time FROM check_ins ORDER BY id DESC LIMIT 5').fetchall()
for c in checkins:
    print(f"  ID: {c[0]}, Member: {c[1]}, In: {c[2]}, Out: {c[3]}")

print("\n=== EQUIPMENT ===")
equipment = cursor.execute('SELECT * FROM equipment').fetchall()
for e in equipment:
    print(f"  ID: {e[0]}, Name: {e[1]}, Type: {e[2]}, Available: {e[3]}")

print("\n=== EQUIPMENT SESSIONS (Recent 3) ===")
sessions = cursor.execute('SELECT id, member_id, equipment_id, start_time, end_time FROM equipment_sessions ORDER BY id DESC LIMIT 3').fetchall()
for s in sessions:
    print(f"  Session ID: {s[0]}, Member: {s[1]}, Equipment: {s[2]}, Start: {s[3]}, End: {s[4]}")

print("\n=== HEART RATE RECORDS (Recent 5) ===")
hr = cursor.execute('SELECT id, session_id, bpm, measured_at FROM heart_rate_records ORDER BY id DESC LIMIT 5').fetchall()
for h in hr:
    print(f"  Record ID: {h[0]}, Session: {h[1]}, BPM: {h[2]}, Time: {h[3]}")

conn.close()

print("\n✅ Database query complete!")
