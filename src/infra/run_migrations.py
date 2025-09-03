import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

MIGRATIONS_DIR = "infra/migrations"

conn = pyodbc.connect(os.getenv("AZURE_SQL_CONN"))
print("test")
cursor = conn.cursor()

for filename in sorted(os.listdir(MIGRATIONS_DIR)):
    if filename.endswith(".sql"):
        with open(os.path.join(MIGRATIONS_DIR, filename), "r") as f:
            sql = f.read()
            cursor.execute(sql)
            conn.commit()

print("✅ Migrations applied successfully")
