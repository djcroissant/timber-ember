import sqlite3
import os

DB_PATH = 'timber_ember.db'

def init_db():
    print(f"Initializing database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the quotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            category TEXT NOT NULL,
            wood_type TEXT NOT NULL,
            dimensions TEXT NOT NULL,
            finish TEXT NOT NULL,
            addons TEXT,
            estimated_price REAL NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create an index on category and status for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_category ON quotes(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status)')
    
    # Check if we should insert some premium demo data
    cursor.execute('SELECT COUNT(*) FROM quotes')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Seeding database with elegant sample quotes...")
        sample_quotes = [
            (
                "Eleanor Vance",
                "eleanor@example.com",
                "(555) 123-4567",
                "tables",
                "Black Walnut",
                "Length: 84\", Width: 40\", Height: 30\"",
                "Satin Polyurethane",
                "Live Edge, Epoxy Grain Fill, Premium Steel Trapezoid Legs",
                3450.00,
                "Looking to have this dining table by mid-July. I love the dark tones of the walnut and want a natural live edge on both long sides.",
                "Pending"
            ),
            (
                "Marcus Sterling",
                "m.sterling@example.com",
                "(555) 987-6543",
                "cutting-boards",
                "Cherry & Maple End-Grain",
                "Length: 20\", Width: 15\", Thickness: 2\"",
                "Organic Beeswax & Mineral Oil",
                "Deep Juice Groove, Side Hand Grips, Personalized Engraving",
                185.00,
                "Please engrave 'S' in the bottom right corner in a clean serif font. This is a wedding gift.",
                "In Progress"
            ),
            (
                "Dr. Sarah Jenkins",
                "sarah.j@example.com",
                "(555) 456-7890",
                "saunas",
                "Western Red Cedar",
                "Diameter: 6ft, Length: 8ft (6-Person Barrel)",
                "Natural Cedar Oil (Exterior Only)",
                "Harvia Wood-burning Heater, Backrest Ergonomics, Panoramic Half-Moon Window",
                7850.00,
                "Delivery site is in my backyard in Oregon. Access is fairly easy, but we'll need off-loading help.",
                "Pending"
            )
        ]
        
        cursor.executemany('''
            INSERT INTO quotes (name, email, phone, category, wood_type, dimensions, finish, addons, estimated_price, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_quotes)
        
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
