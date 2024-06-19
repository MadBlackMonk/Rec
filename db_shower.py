import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=yourserver;'
    'UID=yourusername;'
    'PWD=yourpassword'
)

cursor = conn.cursor()
cursor.execute("SELECT name FROM sys.databases")

for db in cursor:
    print(db[0])

conn.close()
