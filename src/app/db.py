import pyodbc
import os

def get_connection():
    conn_str = os.getenv("AZURE_SQL_CONN")
    return pyodbc.connect(conn_str)
