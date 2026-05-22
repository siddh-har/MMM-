from flask import Flask
from models import db, Hotel, User
import os

def init_db():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makemymoment.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        Hotel.query.delete() 
        
        # Create default admin if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@makemymoment.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("Default admin user created: admin / admin123")
        
        base_data = [
            # HOTELS & RESORTS
            ("Sayaji Hotel", "Tarabai Park", "Hotel", "High", 4.9, "Premium luxury hotel with high-end suites and world-class hospitality."),
            ("Victor Palace", "Rajarampuri", "Hotel", "Medium", 4.4, "Modern comfort with premium amenities and resort-style atmosphere."),
            ("Hotel Pearl", "New Shahupuri", "Hotel", "Medium", 4.2, "Boutique stay near the heart of the city, perfect for business travelers."),
            ("Maratha Regency", "Tarabai Park", "Resort", "High", 4.5, "Luxury resort experience with traditional Kolhapuri themes and garden views."),
            ("Panchshil", "Shivaji Park", "Hotel", "Low", 3.8, "Budget-friendly clean rooms for quick city visits."),
            ("The Fern Residency", "Tarabai Park", "Resort", "High", 4.6, "Eco-friendly luxury resort with premium spa and rooftop lounge."),
            ("K Tree Hotel", "Shivaji Park", "Hotel", "Medium", 4.3, "Stylish modern hotel with executive suites and fine dining."),
            ("Vrishali Executive", "Tarabai Park", "Hotel", "Medium", 4.4, "Famous for rooftop views and premium hospitality services."),
            ("Hotel Opal", "P-B Highway", "Hotel", "Medium", 4.3, "Strategic location for travelers, famous for its comfort and food."),
            ("Landmark Hotel", "Rajarampuri", "Hotel", "Low", 3.7, "Economical stay option with essential modern facilities."),
            
            # CAFES & RESTAURANTS
            ("Dehati Thali", "Tarabai Park", "Restaurant", "Medium", 4.9, "Authentic Kolhapuri non-veg restaurant, world-famous for its thalis."),
            ("Phadatare Misal", "Udyam Nagar", "Cafe", "Low", 4.8, "Legendary breakfast cafe serving the spiciest misal in Kolhapur."),
            ("Bawada Misal", "Kasaba Bawada", "Cafe", "Low", 4.7, "Old-school cafe known for its unique flavored spicy misal."),
            ("Parakh", "Station Road", "Restaurant", "Medium", 4.8, "Top-rated non-veg restaurant specializing in mutton and chicken thalis."),
            ("Nyaas", "Tarabai Park", "Restaurant", "High", 4.7, "Premium fine-dining restaurant with traditional ambiance."),
            ("Solanki Ice Cream", "Mahadwar Road", "Cafe", "Low", 4.9, "Historic dessert cafe famous for local ice cream flavors."),
            ("Rajabhau Bhel", "Khasbag", "Cafe", "Low", 4.8, "The ultimate street food destination, a spicy bhel paradise."),
            ("Tandoor", "Tarabai Park", "Restaurant", "Medium", 4.5, "North Indian specialty restaurant with a cozy family atmosphere."),
            ("Padma Guest House", "Tarabai Park", "Restaurant", "Medium", 4.7, "Home-style authentic Kolhapuri thalis with a rich heritage."),
            ("Milan Hotel", "Station Road", "Restaurant", "Medium", 4.6, "Famous for its Tambda and Pandhra rassa, a non-veg heaven."),
            ("Garden Cafe", "Shivaji Park", "Cafe", "Low", 4.4, "Cozy open-air cafe for snacks and coffee with friends."),
            ("Spicy Corner", "Rajarampuri", "Cafe", "Low", 4.3, "Trendy spot for quick bites, sandwiches and local snacks."),
            ("The Royal Taste", "New Shahupuri", "Restaurant", "High", 4.6, "Multi-cuisine fine dining with a premium royal decor."),
            ("Kolhapuri Tadka", "Highway", "Restaurant", "Medium", 4.5, "Authentic spices and traditional cooking for the perfect local taste."),
            ("Bakery House", "City Center", "Cafe", "Low", 4.2, "Best place for fresh bakes, cakes and evening tea."),
            ("Blue Lagoon Resort", "Panhala", "Resort", "High", 4.8, "Hilltop resort with panoramic views and luxury villas."),
            ("Serene Stays", "Rankala Lake", "Hotel", "Medium", 4.5, "Peaceful lakeside stay with modern amenities."),
            ("Spice Route", "Shahupuri", "Restaurant", "Medium", 4.4, "Fusion restaurant serving global spices with a local twist."),
            ("The Coffee Bean", "Rajarampuri", "Cafe", "Low", 4.6, "Specialty coffee shop with a cozy library corner."),
            ("Mountain View Inn", "Panhala", "Hotel", "Low", 4.1, "Budget inn with great views and basic comforts."),
            ("Grand Regency", "Tarabai Park", "Hotel", "High", 4.7, "Majestic architecture with royal suites and fine dining."),
            ("Green Garden", "Shivaji Park", "Restaurant", "Medium", 4.3, "Family restaurant specializing in organic and fresh meals."),
            ("Urban Bite", "Cyber Chowk", "Cafe", "Low", 4.2, "Fast-paced cafe for quick snacks and healthy smoothies."),
            ("Royal Palms", "Kasaba Bawada", "Resort", "High", 4.9, "Exclusive resort with private pools and luxury spa."),
            ("Old Town Cafe", "Mahadwar Road", "Cafe", "Low", 4.5, "Vintage themed cafe in the heart of the old city."),
            ("Sunset Point", "Rankala", "Restaurant", "Medium", 4.6, "Romantic dining spot with the best sunset views in town."),
            ("The Heritage", "Tarabai Park", "Hotel", "High", 4.8, "Classic heritage hotel with a rich history and premium service."),
            ("Noodles & More", "Rajarampuri", "Restaurant", "Low", 4.1, "Popular spot for Asian street food and quick bites."),
            ("Wellness Resort", "Radhanagari", "Resort", "High", 4.7, "Nature-focused wellness retreat with yoga and organic food."),
            ("City Lights", "Station Road", "Hotel", "Medium", 4.3, "Modern city hotel perfect for short business trips."),
            ("Pasta Paradise", "New Shahupuri", "Restaurant", "Medium", 4.5, "Authentic Italian flavors in a cozy neighborhood setting."),
            ("The Breakfast Club", "Tarabai Park", "Cafe", "Low", 4.7, "Famous for all-day breakfast and artisan pancakes."),
            ("Luxury Haven", "Tarabai Park", "Hotel", "High", 4.9, "The pinnacle of luxury with personalized butler service."),
            ("Riverside Cafe", "Panchganga", "Cafe", "Low", 4.4, "Relaxing riverside spot for tea and local snacks."),
            ("The Steakhouse", "Rajarampuri", "Restaurant", "High", 4.6, "Premium grill and steakhouse with a modern vibe."),
            ("Stay & Dine", "Highway", "Both", "Medium", 4.5, "Convenient stay and food option for long-distance travelers."),
            ("City Hub", "Shahupuri", "Both", "Medium", 4.4, "Integrated hotel and multi-cuisine restaurant in the city center."),
        ]
        
        images = [
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1551882547-ff43c63fedfe?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1543967354-206756857f09?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1601050633729-1956f4789a21?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1589187151003-0dd3c63b451c?auto=format&fit=crop&w=800&q=80"
        ]

        final_hotels = []
        for i in range(200):
            base = base_data[i % len(base_data)]
            img = images[i % len(images)]
            name = f"{base[0]} { (i // len(base_data)) + 1 }" if i >= len(base_data) else base[0]
            
            # Map price_range to actual price based on user feedback
            pr = base[3]
            import random
            if pr == 'Low':
                price = random.uniform(200, 400)
            elif pr == 'Medium':
                price = random.uniform(400, 700)
            else: # High
                price = random.uniform(700, 1500)
                
            # Assign suitability types
            types_pool = ['solo', 'couple', 'family', 'friends']
            h_type = ", ".join(random.sample(types_pool, random.randint(1, 3)))
            
            # Assign amenities (as a list for JSON)
            amenities_pool = ['WiFi', 'Parking', 'AC', 'Room Service', 'Gym', 'Spa', 'Pool']
            h_amenities = random.sample(amenities_pool, random.randint(2, 5))

            h = Hotel(
                name=name,
                location=base[1],
                category=base[2],
                price=round(price, 2),
                rating=round(base[4] - (i * 0.01) if base[4] > 3.0 else 3.0, 1),
                description=base[5],
                image_url=img,
                google_maps_url="https://goo.gl/maps/example",
                type=h_type,
                amenities=h_amenities,
                food_available=True,
                status='approved'
            )
            final_hotels.append(h)

        db.session.bulk_save_objects(final_hotels)
        db.session.commit()
        print(f"Database initialized with {len(final_hotels)} approved properties.")

if __name__ == "__main__":
    init_db()
