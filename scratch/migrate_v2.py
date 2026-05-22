import sqlite3
import os

db_path = 'instance/makemymoment.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    new_columns = [
        ('famous_for', 'TEXT'),
        ('food_menu', 'TEXT'),
        ('additional_images', 'JSON'),
        ('tags', 'JSON')
    ]
    
    for table in ['hotels', 'hotel_requests']:
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                    print(f"Added column {col_name} to {table}")
                except Exception as e:
                    print(f"Error adding {col_name} to {table}: {e}")
            else:
                print(f"Column {col_name} already exists in {table}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")
else:
    print("Database not found. create_all() will handle it.")
