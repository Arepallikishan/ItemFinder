import pyodbc

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'  # change if using named instance
        'DATABASE=LostFoundAI;'
        'Trusted_Connection=yes;'
    )
    return conn
