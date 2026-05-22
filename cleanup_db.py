from flask import Flask
from models import db, Hotel
import os

def cleanup_db():
    app = Flask(__name__)
    db_path = os.path.abspath('instance/makemymoment.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Get all hotels
        all_hotels = Hotel.query.all()
        print(f"Total hotels before cleanup: {len(all_hotels)}")

        seen = set()
        to_delete = []

        import re

        for hotel in all_hotels:
            # Strip trailing space and numbers like " 1", " 2", etc.
            base_name = re.sub(r'\s+\d+$', '', hotel.name).strip()
            key = (base_name.lower(), hotel.location.strip().lower())
            
            if key in seen:
                to_delete.append(hotel)
            else:
                seen.add(key)
                # Also update the name to remove the number if it was there
                if hotel.name != base_name:
                    hotel.name = base_name

        for hotel in to_delete:
            db.session.delete(hotel)

        db.session.commit()
        print(f"Removed {len(to_delete)} duplicate hotels.")
        print(f"Total hotels after cleanup: {len(seen)}")

if __name__ == "__main__":
    cleanup_db()
