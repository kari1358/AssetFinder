import sqlite3

def create_database():
    # Connect to a database (or create one if it doesn't exist)
    conn = sqlite3.connect('reviews.db')
    # Create a 'cursor' for executing commands
    c = conn.cursor()
    # Create a new table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Reviews(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_url TEXT,
            page_id TEXT,
            name TEXT,
            description_content TEXT,
            review TEXT
        );
    ''')
    # Save (commit) the changes
    conn.commit()
    # Close the connection
    conn.close()

def insert_into_database(item_url, page_id, name, description_content, review):
    # Connect to a database (or create one if it doesn't exist)
    conn = sqlite3.connect('reviews.db')
    # Create a 'cursor' for executing commands
    c = conn.cursor()
    # Insert data
    c.execute('''
        INSERT INTO Reviews (item_url, page_id, name, description_content, review)
        VALUES (?, ?, ?, ?, ?);
    ''', (item_url, page_id, name, description_content, review,))
    # Save (commit) the changes
    conn.commit()
    # Close the connection
    conn.close()

# Call the function to create the database
create_database()
