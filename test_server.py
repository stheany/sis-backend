import oracledb
import sys

# DATABASE DETAILS
HOST = '172.16.17.197'
PORT = 1521
SERVICE_NAME = 'SISDB'
USER = 'SISAPP'
PASSWORD = 'SISAPP'

try:
    print(f"🕒 Connecting to {HOST} using THIN MODE (No libraries needed)...")
    
    # THIN MODE: No init_oracle_client() call!
    conn = oracledb.connect(
        user=USER, 
        password=PASSWORD, 
        host=HOST, 
        port=PORT, 
        service_name=SERVICE_NAME
    )
    
    print("✅ SUCCESS! Connected to Oracle SISDB.")
    
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM all_tables WHERE owner = 'SISAPP' AND table_name = 'SYSTEM'")
    row = cursor.fetchone()
    if row:
        print(f"📡 Found SYSTEM table: {row[0]}")
    
    cursor.close()
    conn.close()

except oracledb.Error as e:
    print(f"❌ DATABASE ERROR: {e}")
except Exception as e:
    print(f"⚠️ SYSTEM ERROR: {str(e)}")
