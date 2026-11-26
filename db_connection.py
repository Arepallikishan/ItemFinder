import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{{os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
        f"SERVER={os.getenv('DB_SERVER', 'localhost')};"
        f"DATABASE={os.getenv('DB_NAME', 'LostFoundAI')};"
        "Trusted_Connection=yes;"
    )
    return conn
