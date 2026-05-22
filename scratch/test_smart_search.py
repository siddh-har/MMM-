import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_search(query):
    print(f"\nSearching for: '{query}'")
    try:
        response = requests.get(f"{BASE_URL}/api/search?q={query}")
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results)} results.")
            for i, res in enumerate(results[:3]):
                print(f"  {i+1}. {res['name']} ({res['category']}) - {res['matchPercentage']}% Match")
                if res.get('recommendationReasons'):
                    print(f"     Reasons: {', '.join(res['recommendationReasons'])}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to server: {e}. (Make sure app.py is running)")

if __name__ == "__main__":
    # Test cases representing user requests
    queries = [
        "budget hotels",
        "luxury resort",
        "peaceful stay in nature",
        "best biryani hotel",
        "romantic place for couple",
        "pool resort",
        "cheap veg food",
        "5 star stay"
    ]
    
    print("Starting Smart Search Verification...")
    for q in queries:
        test_search(q)
