from flask import Flask
from models import db, Hotel
import os

def check_categories():
    app = Flask(__name__)
    db_path = os.path.abspath('instance/makemymoment.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)

    with app.app_context():
        hotels = Hotel.query.all()
        categories = set(h.category for h in hotels)
        print(f"Categories: {categories}")
        
        # Check first few hotels
        for h in hotels[:5]:
            print(f"Name: {h.name}, Category: {h.category}, Description: {h.description}")

if __name__ == "__main__":
    check_categories()
