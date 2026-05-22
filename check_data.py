from flask import Flask
from models import db, Hotel
import os
from collections import Counter

def check_duplicates():
    app = Flask(__name__)
    db_path = os.path.abspath('instance/makemymoment.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)

    with app.app_context():
        hotels = Hotel.query.all()
        names = [h.name for h in hotels]
        counts = Counter(names)
        duplicates = {name: count for name, count in counts.items() if count > 1}
        
        print("Duplicates found by name:")
        for name, count in duplicates.items():
            print(f"'{name}': {count} times")
            # Show locations for these duplicates
            locs = [h.location for h in hotels if h.name == name]
            print(f"  Locations: {locs}")

if __name__ == "__main__":
    check_duplicates()
