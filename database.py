import sqlite3

conn = sqlite3.connect("stock.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS stock")
cursor.execute("""
    CREATE TABLE stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compartment TEXT,
        item TEXT,
        status TEXT,
        count INTEGER DEFAULT 0,
        image TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
conn.close()
print("Database ready!")