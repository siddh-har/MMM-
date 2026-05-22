import sys
import os
from flask import Flask
import json

# Add root to sys path
sys.path.append(os.getcwd())
from models import db, Hotel, User

def test_api():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makemymoment.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'test'
    db.init_app(app)

    with app.app_context():
        # Find an admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("No admin user found for testing")
            return

        # Find a hotel
        hotel = Hotel.query.first()
        if not hotel:
            print("No hotel found for testing")
            return

        print(f"Testing GET /api/hotels/{hotel.id}")
        
        # Import the route
        from app import get_hotel
        from flask_login import login_user
        from unittest.mock import MagicMock
        import app as app_module

        # Mock current_user
        app_module.current_user = admin

        with app.test_request_context():
            response = get_hotel(hotel.id)
            data = json.loads(response.data)
            
            print("Response Data:")
            print(json.dumps(data, indent=2))
            
            # Verify fields
            expected_fields = ['id', 'name', 'location', 'category', 'price', 'rating', 'image_url', 'google_maps_url', 'description', 'famous_for', 'food_menu', 'tags', 'one_night_charge', 'type']
            for field in expected_fields:
                if field not in data:
                    print(f"MISSING FIELD: {field}")
                else:
                    print(f"OK: {field}")

if __name__ == "__main__":
    test_api()
