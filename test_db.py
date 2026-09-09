import os
import cx_Oracle

user = os.getenv("DB_USERNAME")
pwd  = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "1521")
svc  = os.getenv("DB_SERVICE_NAME")

dsn  = cx_Oracle.makedsn(host, port, service_name=svc)
conn = cx_Oracle.connect(user=user, password=pwd, dsn=dsn)
cur  = conn.cursor()

cur.execute("SELECT column_name FROM all_tab_columns WHERE table_name = 'USERS_LOGIN_SIS' ORDER BY column_id")
print("Columns:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT * FROM USERS_LOGIN_SIS WHERE ROWNUM <= 3")
print("Users:", cur.fetchall())

conn.close()


