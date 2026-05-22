
# Mock search logic for testing before applying to app.py
import json

class MockHotel:
    def __init__(self, id, name, category, price, rating, amenities, tags, description, famous_for, food_menu, type):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.rating = rating
        self.amenities = amenities
        self.tags = tags
        self.description = description
        self.famous_for = famous_for
        self.food_menu = food_menu
        self.type = type
        self.location = "Kolhapur"
        self.image_url = ""
        self.google_maps_url = ""

# Mock Data (Representative of real data)
mock_hotels = [
    MockHotel(1, "Sayaji Hotel", "Both", 4500, 4.8, ["Pool", "Gym", "Wifi"], ["Luxury", "Business"], "Premium stay in Kolhapur", "Luxury and service", "Multi-cuisine", "Solo, Couple, Family, Friends"),
    MockHotel(2, "Hotel Atria", "Stay", 1500, 4.0, ["Wifi"], ["Budget"], "Affordable stay", "Budget friendly", None, "Solo, Friends"),
    MockHotel(3, "Niyaaz", "Food", 400, 4.6, ["Veg", "Non-Veg"], ["Famous", "Biryani"], "Authentic biryani", "Biryani", "Biryani, Kebabs", "Family, Friends"),
    MockHotel(4, "Solanki Ice Cream", "Food", 150, 4.8, ["Veg"], ["Dessert"], "Best ice cream", "Ice cream", "Ice cream, Shakes", "All"),
    MockHotel(5, "Hotel Chiranjeevi", "Both", 1200, 3.5, ["Wifi"], ["Budget"], "Simple stay and food", "Traditional food", "Local thali", "Family"),
    MockHotel(6, "Dehati", "Food", 300, 4.5, ["Non-Veg"], ["Authentic"], "Authentic Kolhapuri food", "Mutton thali", "Thalis", "All"),
    MockHotel(7, "Rooftop Cafe", "Food", 600, 4.2, ["Veg", "Coffee"], ["Romantic", "View"], "Romantic rooftop dining", "Ambience", "Continental", "Couple, Friends"),
    MockHotel(8, "Family Garden Restaurant", "Food", 500, 4.0, ["Veg", "Play Area"], ["Family"], "Perfect for families", "Garden seating", "Indian", "Family"),
    MockHotel(9, "Business Inn", "Stay", 2500, 4.1, ["Wifi", "Conference Room"], ["Business"], "Corporate stay", "Business amenities", None, "Solo, Business"),
    MockHotel(10, "Pool Side Resort", "Stay", 3500, 4.3, ["Pool", "Spa"], ["Resort", "Luxury"], "Relaxing resort", "Pool", None, "Couple, Family")
]

def search_logic(query_raw, hotels):
    query = query_raw.lower()
    tokens = query.split()
    
    # 1. Semantic Expansion & Intent Mapping
    SEMANTIC_MAP = {
        'budget': ['budget', 'cheap', 'affordable', 'pocket friendly', 'low cost', 'value'],
        'luxury': ['luxury', 'premium', 'elite', 'high end', '5 star', 'expensive', 'royal'],
        'stay': ['stay', 'hotel', 'resort', 'lodge', 'accommodation', 'villa', 'room', 'hostel'],
        'food': ['food', 'restaurant', 'cafe', 'dining', 'eat', 'dinner', 'lunch', 'meal', 'breakfast'],
        'veg': ['veg', 'vegetarian', 'pure veg', 'herbivore'],
        'pool': ['pool', 'swimming', 'water'],
        'romantic': ['romantic', 'couple', 'date', 'honeymoon', 'candlelight'],
        'family': ['family', 'kids', 'children', 'parent', 'group'],
        'business': ['business', 'corporate', 'meeting', 'work', 'official']
    }
    
    # Detect active intents
    active_intents = {}
    for intent, synonyms in SEMANTIC_MAP.items():
        if any(s in query for s in synonyms):
            active_intents[intent] = True

    results = []
    exact_match_hotel = None

    for h in hotels:
        score = 0
        reasons = []
        
        h_name = h.name.lower()
        h_desc = (h.description or "").lower()
        h_famous = (h.famous_for or "").lower()
        h_cat = h.category.lower()
        h_tags = [t.lower() for t in h.tags] if h.tags else []
        h_amenities = [a.lower() for a in h.amenities] if h.amenities else []
        h_menu = (h.food_menu or "").lower()
        h_type = (h.type or "").lower()

        # A. Exact Hotel Priority (Goal 3)
        if query == h_name:
            score += 2000
            reasons.append("Exact search match")
            exact_match_hotel = h
        elif query in h_name:
            score += 800
            reasons.append("Matches hotel name")

        # B. Intent-Aware Scoring (Goal 1 & 2)
        if 'stay' in active_intents and any(k in h_cat for k in ['stay', 'both']):
            score += 200
        if 'food' in active_intents and any(k in h_cat for k in ['food', 'both']):
            score += 200
            
        if 'budget' in active_intents:
            if h.price < 2000: # Simple threshold for mock
                score += 300
                reasons.append("Budget friendly")
        if 'luxury' in active_intents:
            if h.price >= 3000:
                score += 300
                reasons.append("Premium luxury choice")
        if 'veg' in active_intents:
            if 'veg' in h_amenities or 'veg' in h_desc or 'veg' in h_menu:
                score += 300
                reasons.append("Vegetarian options available")
        if 'pool' in active_intents:
            if 'pool' in h_amenities or 'pool' in h_desc or 'pool' in h_famous:
                score += 300
                reasons.append("Swimming pool available")
        if 'family' in active_intents:
            if 'family' in h_type or 'family' in h_tags or 'family' in h_desc:
                score += 300
                reasons.append("Great for family")
        if 'romantic' in active_intents:
            if 'couple' in h_type or 'romantic' in h_tags or 'romantic' in h_desc:
                score += 300
                reasons.append("Romantic atmosphere")
        if 'business' in active_intents:
            if 'business' in h_tags or 'business' in h_desc or 'business' in h_type:
                score += 300
                reasons.append("Ideal for business")

        # C. Keyword Matching
        match_count = sum(1 for t in tokens if t in h_name or t in h_desc or t in h_famous or any(t in tag for tag in h_tags))
        score += match_count * 50

        # D. Rating Modifier
        score += (h.rating - 3.0) * 100

        if score > 100:
            results.append({
                'id': h.id,
                'name': h.name,
                'score': score,
                'reasons': list(dict.fromkeys(reasons))
            })

    # Sort results
    results.sort(key=lambda x: x['score'], reverse=True)

    # E. Similar Hotels Logic (Goal 4)
    if exact_match_hotel:
        similar = []
        for h in hotels:
            if h.id == exact_match_hotel.id: continue
            sim_score = 0
            if h.category == exact_match_hotel.category: sim_score += 100
            price_diff = abs(h.price - exact_match_hotel.price) / (exact_match_hotel.price or 1)
            if price_diff < 0.3: sim_score += 100
            shared_tags = set(h.tags or []) & set(exact_match_hotel.tags or [])
            sim_score += len(shared_tags) * 50
            if sim_score >= 100:
                similar.append({
                    'id': h.id,
                    'name': h.name,
                    'score': sim_score,
                    'reasons': [f"Similar to {exact_match_hotel.name}"]
                })
        similar.sort(key=lambda x: x['score'], reverse=True)
        # Goal 3: Show exact match first, then similar hotels underneath
        # We need to filter out the similar ones if they are already in results, 
        # or just re-order them.
        final_results = [r for r in results if r['id'] == exact_match_hotel.id]
        sim_ids = [s['id'] for s in similar[:3]]
        final_results.extend([s for s in similar[:3]])
        # Add the rest of original results that aren't the exact match or similar
        final_results.extend([r for r in results if r['id'] != exact_match_hotel.id and r['id'] not in sim_ids])
        return final_results

    return results

# Test Queries
test_queries = ["budget stay", "luxury resort", "veg food", "Sayaji Hotel", "rooftop cafe", "family stay", "pool hotel"]

for q in test_queries:
    print(f"\nQuery: '{q}'")
    res = search_logic(q, mock_hotels)
    for r in res[:5]:
        print(f" - {r['name']} (Score: {r['score']}) | Reasons: {r['reasons']}")
