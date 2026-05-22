import sqlite3

def migrate():
    conn = sqlite3.connect('instance/makemymoment.db')
    cursor = conn.cursor()

    print("Starting migration...")

    # Add one_night_charge to hotels
    try:
        cursor.execute('ALTER TABLE hotels ADD COLUMN one_night_charge FLOAT')
        print("Added one_night_charge to hotels table.")
    except sqlite3.OperationalError:
        print("Column one_night_charge already exists in hotels table or table doesn't exist.")

    # Add one_night_charge to hotel_requests
    try:
        cursor.execute('ALTER TABLE hotel_requests ADD COLUMN one_night_charge FLOAT')
        print("Added one_night_charge to hotel_requests table.")
    except sqlite3.OperationalError:
        print("Column one_night_charge already exists in hotel_requests table or table doesn't exist.")

    # Add contact_email to hotel_requests
    try:
        cursor.execute('ALTER TABLE hotel_requests ADD COLUMN contact_email VARCHAR(120)')
        print("Added contact_email to hotel_requests table.")
    except sqlite3.OperationalError:
        print("Column contact_email already exists in hotel_requests table or table doesn't exist.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
