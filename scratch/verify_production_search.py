import sys
import os
from flask import Flask
import json

# Add root to sys path to import models
sys.path.append(os.getcwd())
from models import db, Hotel

def verify_search():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makemymoment.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Import the search logic from app.py
    # Since it's in a route, we can't easily import it without starting the app,
    # but we can simulate the API call or just copy the logic if needed.
    # Actually, let's just use the logic we just wrote in app.py by mocking the request context.
    
    from app import get_search_results

    with app.app_context():
        test_queries = [
            "budget stay",
            "luxury resort",
            "veg food",
            "Sayaji",
            "rooftop cafe",
            "family stay",
            "pool hotel"
        ]

        print("=== PRODUCTION SEARCH VERIFICATION ===")
        for q in test_queries:
            # Mock the request args
            with app.test_request_context(f'/api/search?q={q}'):
                # We need to mock current_user since it's used in get_search_results
                from flask_login import login_user
                from models import User
                # Just mock a dummy user or handled unauthenticated case
                from unittest.mock import MagicMock
                import app as app_module
                app_module.current_user = MagicMock(is_authenticated=False)
                
                response = get_search_results()
                results = json.loads(response.data)
                
                print(f"\nQuery: '{q}'")
                if not results:
                    print("  No results found.")
                    continue
                
                for i, r in enumerate(results[:5]):
                    match_info = f"({r.get('matchPercentage', 0)}%)" if r.get('matchPercentage') else ""
                    reasons = ", ".join(r.get('recommendationReasons', []))
                    print(f"  {i+1}. {r['name']} {match_info} | Price: {r['price']} | Reasons: {reasons}")

if __name__ == "__main__":
    verify_search()
