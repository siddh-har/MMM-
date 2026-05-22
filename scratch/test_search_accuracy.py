import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_accuracy(query):
    print(f"\n[TEST] Query: '{query}'")
    try:
        response = requests.get(f"{BASE_URL}/api/search?q={query}")
        if response.status_code == 200:
            results = response.json()
            if not results:
                print("  No results found.")
                return
            
            print(f"  Total results: {len(results)}")
            # Check top 3 for category consistency
            for i, res in enumerate(results[:5]):
                cat = res.get('category', 'Unknown')
                score = res.get('relevance_score', 0)
                print(f"  {i+1}. {res['name']} | Category: {cat} | Match: {res['matchPercentage']}%")
        else:
            print(f"  Error: {response.status_code}")
    except Exception as e:
        print(f"  Connection Error: {e}")

if __name__ == "__main__":
    print("=== SEARCH ACCURACY VERIFICATION ===")
    
    # Test cases for category separation
    scenarios = [
        "budget stay",        # Should show 'Stay' or 'Both'
        "best biryani",      # Should show 'Food' or 'Both'
        "cheap food",        # Should show 'Food' or 'Both'
        "luxury resort",     # Should show 'Stay' or 'Both'
        "romantic dinner",   # Should show 'Food' or 'Both'
        "family stay",       # Should show 'Stay' or 'Both'
        "pocket friendly hotel" # Should show 'Stay' or 'Both'
    ]
    
    for s in scenarios:
        test_accuracy(s)
