import sqlite3

def check_database():
    # Connect to the database
    conn = sqlite3.connect('reviews.db')
    # Create a cursor
    c = conn.cursor()
    # Execute a command to get the table info
    c.execute("PRAGMA table_info(Reviews);")
    # Print each column name and type
    columns = c.fetchall()
    for column in columns:
        print(f"{column[1]}: {column[2]}")
    # Close the connection
    conn.close()

check_database()
