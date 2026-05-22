import json
from app import app
from flask import request

def test_recommendations():
    params = {
        "category": "Stay",
        "budget": "Medium",
        "group_type": "Family",
        "duration": "3+ Nights",
        "food_type": "Veg"
    }
    
    with app.test_request_context(query_string=params):
        from app import get_recommendations
        response = get_recommendations()
        data = json.loads(response.get_data(as_text=True))
        
        print(f"Results found: {len(data)}")
        if data:
            print("Top 3 Recommendations:")
            for h in data[:3]:
                print(f"- {h['name']} (Score: {h['score']}, Match: {h['matchPercentage']}%, Price: {h['price']})")
                print(f"  Category: {h['category']}, Suitability: {h['suitability']}")

if __name__ == "__main__":
    test_recommendations()
