import os
import pyodbc
from app.config import get_settings

settings = get_settings()

MIGRATIONS_DIR = "infra/migrations"

conn = pyodbc.connect(settings.AZURE_SQL_CONN)

cursor = conn.cursor()

for filename in sorted(os.listdir(MIGRATIONS_DIR)):
    if filename.endswith(".sql"):
        with open(os.path.join(MIGRATIONS_DIR, filename), "r") as f:
            sql = f.read()
            cursor.execute(sql)
            conn.commit()

print("✅ Migrations applied successfully")
