from flask import Flask
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, Hotel

def list_hotels():
    app = Flask(__name__)
    # The app.py uses 'sqlite:///makemymoment.db' which usually resolves to project root or instance folder
    # Looking at app.py: app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makemymoment.db'
    # By default Flask-SQLAlchemy looks in the instance folder if not specified, 
    # but app.py doesn't seem to specify instance_relative_config=True.
    # However, list_dir showed 'makemymoment.db' in the root.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makemymoment.db'
    db.init_app(app)

    with app.app_context():
        hotels = Hotel.query.all()
        print(f"Total hotels: {len(hotels)}")
        for h in hotels[:20]:
            print(f"ID: {h.id} | Name: {h.name} | Category: {h.category} | Rating: {h.rating} | Tags: {h.tags} | Price: {h.price}")

if __name__ == "__main__":
    list_hotels()
