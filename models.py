from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(100)) # e.g., 'solo, couple, family, friends'
    amenities = db.Column(db.JSON) # JSON field for amenities
    food_available = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='approved') # 'approved' or 'pending'
    
    # Keeping these for UI compatibility
    category = db.Column(db.String(50), nullable=False) # 'Stay', 'Food', 'Both'
    image_url = db.Column(db.String(255))
    google_maps_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New detailed fields
    famous_for = db.Column(db.Text, nullable=True)
    food_menu = db.Column(db.Text, nullable=True)
    additional_images = db.Column(db.JSON, nullable=True) # List of URLs
    tags = db.Column(db.JSON, nullable=True) # List of tags
    one_night_charge = db.Column(db.Float, nullable=True) # Specific for Stay/Both

class HotelRequest(db.Model):
    __tablename__ = 'hotel_requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(100))
    amenities = db.Column(db.JSON)
    food_available = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='pending')
    
    # UI compatibility fields
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    google_maps_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New detailed fields
    famous_for = db.Column(db.Text, nullable=True)
    food_menu = db.Column(db.Text, nullable=True)
    additional_images = db.Column(db.JSON, nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    one_night_charge = db.Column(db.Float, nullable=True)
    contact_email = db.Column(db.String(120))

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
