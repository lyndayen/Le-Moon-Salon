import sqlite3

def init_db():
    # This creates the file 'salon.db' automatically
    conn = sqlite3.connect('salon.db')
    c = conn.cursor()

    # Table 1: Customer Info
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 name TEXT NOT NULL, 
                 phone TEXT NOT NULL)''')

    # Table 2: Point Balances
    c.execute('''CREATE TABLE IF NOT EXISTS balances (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 customer_id INTEGER,
                 package_name TEXT,
                 remaining_points INTEGER,
                 total_points INTEGER,
                 FOREIGN KEY(customer_id) REFERENCES customers(id))''')

    # Table 3: Transaction History (For Power BI)
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 customer_id INTEGER,
                 service_type TEXT,
                 date_used DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()
    print("Database and Tables Created Successfully!")

if __name__ == "__main__":
    init_db()
    