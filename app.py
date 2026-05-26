from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Hotel, HotelRequest, User, SearchHistory
from sqlalchemy import or_, and_, desc
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-make-my-moment'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makemymoment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'signin'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper to save uploaded files (Main image, Menu, Additional images)
def save_uploaded_file(file):
    if not file or file.filename == '':
        return None
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    # Add timestamp to prevent name collisions
    filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return f'/static/uploads/{filename}'

@app.route('/')
def index():
    featured_hotels = []
    section_title = "Featured"
    section_subtitle = "Destinations."
    
    if current_user.is_authenticated and session.get('preferred_category'):
        pref_cat = session.get('preferred_category')
        # Fetch 4 top-rated preferred category and 2 other top-rated
        pref_hotels = Hotel.query.filter(Hotel.status=='approved', Hotel.category==pref_cat).order_by(desc(Hotel.rating)).limit(4).all()
        pref_ids = [h.id for h in pref_hotels]
        other_hotels = Hotel.query.filter(Hotel.status=='approved', ~Hotel.id.in_(pref_ids)).order_by(desc(Hotel.rating)).limit(6 - len(pref_hotels)).all()
        featured_hotels = pref_hotels + other_hotels
        
        # Determine title based on preference
        if pref_cat == 'Food':
            section_title = "Picked for"
            section_subtitle = "Your Taste."
        elif pref_cat == 'Stay':
            section_title = "Perfect for"
            section_subtitle = "Your Stay."
        else:
            section_title = "Recommended"
            section_subtitle = "For You."
    else:
        featured_hotels = Hotel.query.filter_by(status='approved').order_by(desc(Hotel.rating)).limit(6).all()
        
    return render_template('index.html', featured_hotels=featured_hotels, section_title=section_title, section_subtitle=section_subtitle)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        if User.query.count() == 0:
            new_user.role = 'admin'
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('signin.html')

@app.route('/logout')
@login_required
def logout():
    role = current_user.role
    logout_user()
    if role == 'admin':
        return redirect(url_for('admin_login'))
    return redirect(url_for('index'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, role='admin').first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid admin credentials', 'error')
    return render_template('admin_login.html')

@app.route('/partner')
def partner():
    return render_template('partner.html')

@app.route('/api/partner', methods=['POST'])
def submit_partner_request():
    # Use request.form for multipart/form-data
    data = request.form
    
    # Handle Image Upload
    image_url = 'https://images.unsplash.com/photo-1566073771259-6a8506099945'
    image_file = request.files.get('image_file')
    if image_file:
        saved_path = save_uploaded_file(image_file)
        if saved_path: image_url = saved_path

    new_request = HotelRequest(
        name=data.get('hotel_name'),
        location=data.get('location'),
        contact_email=data.get('contact_email'),
        category=data.get('category'),
        price=float(data.get('price')) if data.get('price') else 0.0,
        one_night_charge=float(data.get('one_night_charge')) if data.get('one_night_charge') else None,
        type=data.get('type'),
        description=data.get('description'),
        google_maps_url=data.get('google_maps_url'),
        famous_for=data.get('famous_for'),
        tags=[tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()],
        image_url=image_url,
        status='pending'
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Request submitted successfully!'})

@app.route('/flow')
def flow():
    featured_hotels = []
    section_title = "Featured"
    section_subtitle = "Destinations."
    
    if current_user.is_authenticated and session.get('preferred_category'):
        pref_cat = session.get('preferred_category')
        pref_hotels = Hotel.query.filter(Hotel.status=='approved', Hotel.category==pref_cat).order_by(desc(Hotel.rating)).limit(4).all()
        pref_ids = [h.id for h in pref_hotels]
        other_hotels = Hotel.query.filter(Hotel.status=='approved', ~Hotel.id.in_(pref_ids)).order_by(desc(Hotel.rating)).limit(6 - len(pref_hotels)).all()
        featured_hotels = pref_hotels + other_hotels
        
        if pref_cat == 'Food':
            section_title = "Picked for"
            section_subtitle = "Your Taste."
        elif pref_cat == 'Stay':
            section_title = "Perfect for"
            section_subtitle = "Your Stay."
        else:
            section_title = "Recommended"
            section_subtitle = "For You."
    else:
        featured_hotels = Hotel.query.filter_by(status='approved').order_by(desc(Hotel.rating)).limit(6).all()
        
    return render_template('flow.html', featured_hotels=featured_hotels, section_title=section_title, section_subtitle=section_subtitle)

# System 1: Quiz Recommendations
@app.route('/api/quiz-recommendations')
def get_quiz_recommendations():
    user_cat = request.args.get('category', '').lower()
    budget_pref = request.args.get('budget', '').lower()
    user_group = request.args.get('group_type', '').lower()
    food_pref = request.args.get('food_type', '').lower()
    user_amenities = request.args.getlist('amenities')
    
    all_hotels = Hotel.query.filter_by(status='approved').all()
    if not all_hotels:
        return jsonify([])

    # Price stats for normalization
    prices = [h.price for h in all_hotels if h.price > 0]
    min_price, max_price = (min(prices), max(prices)) if prices else (100, 5000)
    avg_price = sum(prices) / len(prices) if prices else 1000

    results = []
    for h in all_hotels:
        score = 0
        reasons = []
        
        h_cat = h.category.lower() if h.category else ""
        h_type = h.type.lower() if h.type else ""
        h_amenities = [a.lower() for a in h.amenities] if isinstance(h.amenities, list) else []
        h_desc = (h.description or "").lower()
        h_famous = (h.famous_for or "").lower()
        h_tags = [t.lower() for t in h.tags] if h.tags else []

        # 1. Category Matching (Weight: 50 - High Priority)
        # ---------------------------------------------------------
        if user_cat:
            cat_match = False
            if user_cat == 'stay' and any(k in h_cat for k in ['hotel', 'resort', 'stay', 'both']): cat_match = True
            if user_cat == 'food' and any(k in h_cat for k in ['cafe', 'restaurant', 'food', 'both']): cat_match = True
            
            if cat_match:
                score += 50
                reasons.append(f"Ideal for {user_cat.capitalize()}")
            else:
                score -= 30 # Soft penalty instead of strict filter for fallback support

        # 2. Budget/Price Relevance (Weight: 40)
        # ---------------------------------------------------------
        budget_score = 0
        if 'low' in budget_pref or 'pocket' in budget_pref:
            if h.price <= avg_price:
                budget_score = 40 * (1 - (h.price - min_price) / (avg_price - min_price + 1))
            else:
                budget_score = -20
        elif 'luxury' in budget_pref or 'high' in budget_pref:
            if h.price >= avg_price:
                budget_score = 40 * ((h.price - avg_price) / (max_price - avg_price + 1))
            else:
                budget_score = -20
        else: # Medium
            diff = abs(h.price - avg_price)
            budget_score = max(0, 40 - (diff / (avg_price + 1) * 40))
            
        score += budget_score
        if budget_score > 25: reasons.append("Perfectly fits your budget")

        # 3. Tags Matching (Weight: 35) & Group Type
        # ---------------------------------------------------------
        tag_score = 0
        user_intents = set()
        if budget_pref: user_intents.add(budget_pref)
        if user_group: user_intents.add(user_group)
        if food_pref and food_pref != 'any': user_intents.add(food_pref)
        
        # Also add semantic vibes to intents
        if user_group == 'family': user_intents.update(['safe', 'spacious', 'kids', 'peaceful', 'children'])
        if user_group == 'couple': user_intents.update(['romantic', 'private', 'quiet', 'honeymoon', 'candle'])
        if user_group == 'friends': user_intents.update(['party', 'music', 'fun', 'group', 'spacious'])

        matched_tags = 0
        for intent in user_intents:
            if any(intent in t for t in h_tags) or intent in h_desc or intent in h_famous or intent in h_type:
                matched_tags += 1
                
        if matched_tags > 0:
            tag_score = min(35, matched_tags * 10)
            score += tag_score
            if user_group and (user_group in h_tags or user_group in h_type):
                reasons.append(f"Great for {user_group.capitalize()}")
            elif matched_tags > 1:
                reasons.append("Matches your preferred vibes")

        # 4. Amenities Match (Weight: 25)
        # ---------------------------------------------------------
        if user_amenities:
            match_count = sum(1 for am in user_amenities if am.lower() in h_amenities)
            if match_count > 0:
                score += (match_count / len(user_amenities)) * 25
                reasons.append(f"Has requested amenities")

        # 5. Food Preference Specific Check
        # ---------------------------------------------------------
        if food_pref and food_pref != 'any':
            h_menu = (h.food_menu or "").lower()
            if food_pref in h_menu or food_pref in h_desc:
                score += 15
                if not any("food" in r.lower() for r in reasons):
                    reasons.append(f"Specializes in {food_pref.capitalize()} food")
            elif h.food_available:
                score += 5

        # 6. Global Modifiers (Rating) (Weight: 10)
        # ---------------------------------------------------------
        rating_bonus = (h.rating - 3.0) * 5 if h.rating >= 3.0 else -10
        score += min(10, rating_bonus)

        # Match Percentage Calculation
        # Max score is approx 50 + 40 + 35 + 25 + 15 + 10 = 175
        match_percentage = min(100, max(0, round((score / 175) * 100, 1)))

        # Only include if score > -30 (filters out extreme mismatches but allows soft fallback)
        if score > -30:
            results.append({
                'id': h.id, 'name': h.name, 'price': h.price, 'rating': h.rating,
                'location': h.location, 'category': h.category, 'image_url': h.image_url,
                'description': h.description, 'score': score, 'matchPercentage': match_percentage,
                'recommendationReasons': list(dict.fromkeys(reasons))[:3],
                'google_maps_url': h.google_maps_url, 'type': h.type
            })

    # Sort by Score (Primary) then Rating
    results.sort(key=lambda x: (x['score'], x['rating']), reverse=True)
    
    # Fallback Mechanism: If top results are poor, add popular items but don't say "No matching results"
    if not results or (len(results) > 0 and results[0]['score'] < 10):
        popular = Hotel.query.filter_by(status='approved').order_by(desc(Hotel.rating)).limit(5).all()
        for p in popular:
            if not any(r['id'] == p.id for r in results[:5]):
                results.append({
                    'id': p.id, 'name': p.name, 'price': p.price, 'rating': p.rating,
                    'location': p.location, 'category': p.category, 'image_url': p.image_url,
                    'description': p.description, 'score': 0, 'matchPercentage': 0,
                    'recommendationReasons': ["Highly recommended by locals"],
                    'google_maps_url': p.google_maps_url, 'type': p.type
                })

    return jsonify(results[:12])

@app.route('/api/search')
def get_search_results():
    query_raw = request.args.get('q', '').strip()
    if not query_raw:
        return jsonify([])
    
    query = query_raw.lower()
    tokens = query.split()
    
    # 1. Personalization & History (Preserve existing functionality)
    if current_user.is_authenticated:
        new_search = SearchHistory(user_id=current_user.id, query=query_raw)
        db.session.add(new_search)
        db.session.commit()

    # 2. Semantic Mapping & Intent Detection (Goal 1 & 2)
    SEMANTIC_MAP = {
        'budget': ['budget', 'cheap', 'affordable', 'pocket friendly', 'low cost', 'low price', 'value', 'economical'],
        'luxury': ['luxury', 'premium', 'elite', 'high end', '5 star', 'royal', 'expensive', 'exclusive', 'upscale'],
        'stay': ['stay', 'hotel', 'resort', 'lodge', 'accommodation', 'villa', 'room', 'hostel', 'inn', 'suite'],
        'food': ['food', 'restaurant', 'cafe', 'dining', 'eat', 'dinner', 'lunch', 'meal', 'breakfast', 'cuisine', 'bakery'],
        'veg': ['veg', 'vegetarian', 'pure veg', 'herbivore'],
        'pool': ['pool', 'swimming', 'water park', 'aqua'],
        'romantic': ['romantic', 'couple', 'date', 'honeymoon', 'candlelight', 'aesthetic', 'private'],
        'family': ['family', 'kids', 'children', 'parent', 'group', 'friendly'],
        'business': ['business', 'corporate', 'meeting', 'work', 'official', 'conference']
    }
    
    active_intents = {}
    for intent, synonyms in SEMANTIC_MAP.items():
        if any(s in query for s in synonyms):
            active_intents[intent] = True

    # 3. Search & Scoring (Goal 5)
    hotels = Hotel.query.filter_by(status='approved').all()
    results = []
    exact_match_hotel = None

    for h in hotels:
        score = 0
        reasons = []
        h_name, h_cat = h.name.lower(), (h.category or "").lower()
        h_desc, h_famous = (h.description or "").lower(), (h.famous_for or "").lower()
        h_tags = [t.lower() for t in h.tags] if h.tags else []
        h_amenities = [a.lower() for a in h.amenities] if h.amenities else []
        h_menu = (h.food_menu or "").lower()
        h_type = (h.type or "").lower()
        h_loc = h.location.lower()

        # A. Exact Match Priority (Goal 3)
        if query == h_name:
            score += 2000
            reasons.append("Exact search match")
            exact_match_hotel = h
        elif query in h_name:
            score += 800
            reasons.append("Highly relevant name")
        
        # B. Intent & Category Alignment
        if 'stay' in active_intents and any(k in h_cat for k in ['stay', 'hotel', 'resort', 'both']): 
            score += 200
        if 'food' in active_intents and any(k in h_cat for k in ['food', 'restaurant', 'cafe', 'both']): 
            score += 200

        # C. Semantic Vibe Matching
        if 'budget' in active_intents:
            # Check price or tags
            if h.price < 1500 or any(k in h_desc or k in h_famous for k in SEMANTIC_MAP['budget']):
                score += 300
                reasons.append("Great value for money")
        if 'luxury' in active_intents:
            if h.price > 3000 or any(k in h_desc or k in h_famous for k in SEMANTIC_MAP['luxury']):
                score += 300
                reasons.append("Premium luxury experience")
        if 'veg' in active_intents:
            if 'veg' in h_amenities or 'veg' in h_menu or 'veg' in h_name or 'veg' in h_desc:
                score += 400
                reasons.append("Vegetarian friendly")
        if 'pool' in active_intents:
            if 'pool' in h_amenities or 'pool' in h_desc or 'pool' in h_famous:
                score += 400
                reasons.append("Features a swimming pool")
        if 'family' in active_intents:
            if 'family' in h_type or 'family' in h_tags or 'family' in h_desc:
                score += 300
                reasons.append("Ideal for families")
        if 'romantic' in active_intents:
            if 'couple' in h_type or 'romantic' in h_tags or 'romantic' in h_desc:
                score += 300
                reasons.append("Romantic ambiance")
        if 'business' in active_intents:
            if 'business' in h_tags or 'business' in h_desc or 'business' in h_type:
                score += 300
                reasons.append("Business travel friendly")

        # D. Keyword & Location Match
        match_count = 0
        for t in tokens:
            if t in h_name: match_count += 3
            if t in h_loc: match_count += 2
            if t in h_desc or t in h_famous: match_count += 1
            if any(t in tag for tag in h_tags): match_count += 2
            if any(t in am for am in h_amenities): match_count += 2
        
        score += match_count * 40

        # E. Global Modifiers (Rating)
        score += (h.rating - 3.0) * 100

        if score > 150:
            match_percentage = min(100, round((score / 800) * 100, 1)) if score < 1500 else 100
            results.append({
                'id': h.id, 'name': h.name, 'price': h.price, 'rating': h.rating, 'location': h.location,
                'category': h.category, 'image_url': h.image_url, 'description': h.description,
                'relevance_score': score, 'matchPercentage': match_percentage,
                'recommendationReasons': list(dict.fromkeys(reasons))[:3],
                'google_maps_url': h.google_maps_url, 'type': h.type
            })

    # Sort results by score
    results.sort(key=lambda x: x['relevance_score'], reverse=True)

    # 4. Similar Hotels Logic (Goal 4)
    if exact_match_hotel:
        similar_hotels = []
        em_cat = (exact_match_hotel.category or "").lower()
        em_price = exact_match_hotel.price
        em_tags = set(t.lower() for t in exact_match_hotel.tags) if exact_match_hotel.tags else set()
        
        for h in hotels:
            if h.id == exact_match_hotel.id: continue
            
            sim_score = 0
            if (h.category or "").lower() == em_cat: sim_score += 100
            if em_price > 0:
                price_diff = abs(h.price - em_price) / em_price
                if price_diff < 0.3: sim_score += 100
            
            h_tags = set(t.lower() for t in h.tags) if h.tags else set()
            shared_tags = em_tags & h_tags
            sim_score += len(shared_tags) * 50
            
            if abs(h.rating - exact_match_hotel.rating) < 1.0: sim_score += 50
            
            if sim_score >= 150:
                similar_hotels.append({
                    'id': h.id, 'name': h.name, 'price': h.price, 'rating': h.rating, 'location': h.location,
                    'category': h.category, 'image_url': h.image_url, 'description': h.description,
                    'relevance_score': sim_score, 'matchPercentage': 0,
                    'recommendationReasons': [f"Similar to {exact_match_hotel.name}"],
                    'google_maps_url': h.google_maps_url, 'type': h.type
                })
        
        similar_hotels.sort(key=lambda x: (x['relevance_score'], x['rating']), reverse=True)
        # Goal 3: Show exact match first, then similar hotels underneath
        # Results[0] is the exact match. We inject similar ones after it.
        top_res = [r for r in results if r['id'] == exact_match_hotel.id]
        sim_ids = [s['id'] for s in similar_hotels[:4]]
        
        # Build final list: Exact Match -> Similar Hotels -> Other relevant results
        final_list = top_res + similar_hotels[:4]
        for r in results:
            if r['id'] != exact_match_hotel.id and r['id'] not in sim_ids:
                final_list.append(r)
        results = final_list

    # 5. Fallback & No Empty Results (Goal 6)
    if not results and query:
        # Show highly rated hotels as fallback
        top_hotels = Hotel.query.filter_by(status='approved').order_by(desc(Hotel.rating)).limit(6).all()
        return jsonify([{
            'id': h.id, 'name': h.name, 'price': h.price, 'rating': h.rating, 'location': h.location,
            'category': h.category, 'image_url': h.image_url, 'description': h.description,
            'matchPercentage': 0, 'recommendationReasons': ["Highly rated choice"], 'google_maps_url': h.google_maps_url, 'type': h.type
        } for h in top_hotels])
    
    return jsonify(results[:15])

@app.route('/api/recent-searches')
def get_recent_searches():
    if not current_user.is_authenticated:
        return jsonify([])
    searches = db.session.query(SearchHistory).filter_by(user_id=current_user.id).order_by(SearchHistory.created_at.desc()).limit(5).all()
    # Unique queries only
    unique_queries = list(dict.fromkeys([s.query for s in searches]))
    return jsonify(unique_queries)

@app.route('/api/hotels/explore')
def explore_hotels():
    viewed = session.get('viewed_hotels', [])
    all_hotels = Hotel.query.filter_by(status='approved').all()
    
    # Sorting logic:
    # 1. Recently viewed hotels first (newest to oldest)
    # 2. Others by rating
    
    def get_sort_priority(h):
        if h.id in viewed:
            # Position in 'viewed' list. 
            # If viewed = [id1, id2, id3] where id3 is most recent.
            # We want id3 to have highest priority (lowest value for sort key)
            return (0, -viewed.index(h.id))
        return (1, -h.rating)

    sorted_hotels = sorted(all_hotels, key=get_sort_priority)
    
    return jsonify([{
        'id': h.id,
        'name': h.name,
        'price': h.price,
        'rating': h.rating,
        'location': h.location,
        'category': h.category,
        'image_url': h.image_url,
        'description': h.description,
        'google_maps_url': h.google_maps_url,
        'type': h.type
    } for h in sorted_hotels])

@app.route('/hotel/<int:id>')
def hotel_details(id):
    hotel = Hotel.query.get_or_404(id)
    similar_hotels = Hotel.query.filter(
        Hotel.id != hotel.id,
        Hotel.status == 'approved',
        Hotel.location == hotel.location,
        Hotel.category == hotel.category
    ).limit(4).all()
    
    reasons = []
    if hotel.price < 400: reasons.append("Budget friendly choice")
    if hotel.rating >= 4.5: reasons.append("Exceptionally high guest ratings")

    # Track interest
    viewed = session.get('viewed_hotels', [])
    if hotel.id in viewed:
        viewed.remove(hotel.id)
    viewed.append(hotel.id)
    # Keep only last 20
    session['viewed_hotels'] = viewed[-20:]
    
    # Track preferred category for logged in users
    if current_user.is_authenticated:
        h_type = (hotel.type or "").lower()
        if hotel.category == 'Food' or 'cafe' in h_type or 'restaurant' in h_type:
            session['preferred_category'] = 'Food'
        elif hotel.category == 'Stay' or 'hotel' in h_type or 'resort' in h_type:
            session['preferred_category'] = 'Stay'
    
    return render_template('hotel_details.html', hotel=hotel, similar_hotels=similar_hotels, reasons=reasons)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin': return redirect(url_for('index'))
    hotels = Hotel.query.order_by(Hotel.created_at.desc()).all()
    requests = HotelRequest.query.filter_by(status='pending').all()
    users = User.query.all()

    # --- Analytics Calculations ---
    from collections import Counter
    # Search Analytics
    searches = db.session.query(SearchHistory).all()
    search_queries = [s.query.lower() for s in searches]
    top_searches = dict(Counter(search_queries).most_common(5))
    if not top_searches:
        top_searches = {'budget stay': 120, 'veg food': 85, 'luxury resort': 64, 'pool': 45} # Fallback for empty DB
    
    # Hotel Analytics
    approved_hotels = [h for h in hotels if h.status == 'approved']
    total_food = sum(1 for h in approved_hotels if h.category == 'Food')
    total_stay = sum(1 for h in approved_hotels if h.category == 'Stay')
    total_both = sum(1 for h in approved_hotels if h.category == 'Both')
    avg_rating = round(sum(h.rating for h in approved_hotels) / len(approved_hotels), 1) if approved_hotels else 0.0
    
    # Partner Analytics
    all_requests = HotelRequest.query.all()
    pending_reqs = sum(1 for r in all_requests if r.status == 'pending')
    approved_reqs = sum(1 for r in all_requests if r.status == 'approved')
    rejected_reqs = sum(1 for r in all_requests if r.status == 'rejected')
    
    analytics_data = {
        'top_searches': top_searches,
        'hotel_distribution': {'Food': total_food, 'Stay': total_stay, 'Both': total_both},
        'avg_rating': avg_rating,
        'partner_requests': {'Pending': pending_reqs, 'Approved': approved_reqs, 'Rejected': rejected_reqs}
    }

    return render_template('admin.html', hotels=hotels, requests=requests, users=users, analytics_data=analytics_data)

@app.route('/admin/approve/<int:id>', methods=['POST'])
@login_required
def approve_request(id):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    req = HotelRequest.query.get_or_404(id)
    
    # Create new hotel from request
    new_hotel = Hotel(
        name=req.name,
        location=req.location,
        category=req.category,
        price=req.price,
        rating=req.rating,
        image_url=req.image_url or 'https://images.unsplash.com/photo-1566073771259-6a8506099945',
        google_maps_url=req.google_maps_url,
        description=req.description,
        status='approved',
        famous_for=req.famous_for,
        food_menu=req.food_menu,
        additional_images=req.additional_images,
        tags=req.tags,
        one_night_charge=req.one_night_charge,
        type=req.type,
        food_available=req.food_available
    )
    
    req.status = 'approved'
    db.session.add(new_hotel)
    db.session.commit()
    return jsonify({'message': 'Property approved and listed successfully!'})

@app.route('/admin/reject/<int:id>', methods=['POST'])
@login_required
def reject_request(id):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    req = HotelRequest.query.get_or_404(id)
    req.status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Property request rejected.'})

# ---------------------------------------------------------
# ADMIN: Add Hotel Route
# ---------------------------------------------------------
@app.route('/admin/add-hotel', methods=['POST'])
@login_required
def admin_add_hotel():
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    
    # 1. Form Handling: Extract data from multipart/form-data
    data = request.form
    
    # 2. Validation: Ensure price and rating are numeric
    try:
        price = float(data.get('price', 0))
        rating = float(data.get('rating', 0))
        one_night_charge = float(data.get('one_night_charge')) if data.get('one_night_charge') else None
    except ValueError:
        return jsonify({'error': 'Price and Rating must be numeric'}), 400

    # 3. Handle File Uploads (Main Image)
    image_url = data.get('image_url') or 'https://images.unsplash.com/photo-1566073771259-6a8506099945'
    main_file = request.files.get('image_file')
    if main_file:
        saved_path = save_uploaded_file(main_file)
        if saved_path: image_url = saved_path
    
    # Handle Food Menu (Text or Image)
    food_menu = data.get('food_menu')
    menu_file = request.files.get('menu_file')
    if menu_file:
        saved_path = save_uploaded_file(menu_file)
        if saved_path: food_menu = saved_path
    
    # Handle 3 Additional Images
    add_imgs = []
    for i in range(1, 4):
        f = request.files.get(f'add_img_{i}')
        if f:
            saved_path = save_uploaded_file(f)
            if saved_path: add_imgs.append(saved_path)
        
    # Process Tags (comma-separated string to list)
    tags_list = [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()]

    # 4. Database Insertion: Use SQLAlchemy properly
    new_hotel = Hotel(
        name=data.get('name'), 
        location=data.get('location'), 
        category=data.get('category'), 
        price=price, 
        rating=rating, 
        image_url=image_url, 
        google_maps_url=data.get('google_maps_url'), 
        description=data.get('description'),
        status='approved', # Automatically approved when added by admin
        famous_for=data.get('famous_for'),
        food_menu=food_menu,
        additional_images=add_imgs,
        tags=tags_list,
        one_night_charge=one_night_charge,
        type=data.get('type'), 
        food_available=True # Default to true
    )
    
    db.session.add(new_hotel)
    db.session.commit()
    
    # 5. Return success message
    return jsonify({'message': 'Hotel stored in SQLite DB successfully!'})

# ---------------------------------------------------------
# ADMIN: Edit Hotel Route
# ---------------------------------------------------------
@app.route('/admin/edit-hotel/<int:id>', methods=['POST'])
@login_required
def admin_edit_hotel(id):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    h = Hotel.query.get_or_404(id)
    data = request.form
    
    # Validation
    try:
        h.price = float(data.get('price', 0))
        h.rating = float(data.get('rating', 0))
        h.one_night_charge = float(data.get('one_night_charge')) if data.get('one_night_charge') else None
    except ValueError:
        return jsonify({'error': 'Price and Rating must be numeric'}), 400
    
    # Update simple fields
    h.name = data.get('name')
    h.location = data.get('location')
    h.category = data.get('category')
    h.google_maps_url = data.get('google_maps_url')
    h.description = data.get('description')
    h.famous_for = data.get('famous_for')
    
    # Handle File Uploads
    main_file = request.files.get('image_file')
    if main_file:
        saved_path = save_uploaded_file(main_file)
        if saved_path: h.image_url = saved_path
    elif data.get('image_url'):
        h.image_url = data.get('image_url')

    menu_file = request.files.get('menu_file')
    if menu_file:
        saved_path = save_uploaded_file(menu_file)
        if saved_path: h.food_menu = saved_path
    else:
        h.food_menu = data.get('food_menu')
    
    # Update Additional Images if new ones provided
    add_imgs = []
    for i in range(1, 4):
        f = request.files.get(f'add_img_{i}')
        if f:
            saved_path = save_uploaded_file(f)
            if saved_path: add_imgs.append(saved_path)
    if add_imgs:
        h.additional_images = add_imgs
    
    h.tags = [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()]
    h.type = data.get('type')
    
    db.session.commit()
    return jsonify({'message': 'Hotel updated successfully!'})

@app.route('/api/hotels/<int:id>', methods=['GET'])
@login_required
def get_hotel(id):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    h = Hotel.query.get_or_404(id)
    return jsonify({
        'id': h.id,
        'name': h.name,
        'location': h.location,
        'category': h.category,
        'price': h.price,
        'rating': h.rating,
        'image_url': h.image_url,
        'google_maps_url': h.google_maps_url,
        'description': h.description,
        'famous_for': h.famous_for,
        'food_menu': h.food_menu,
        'tags': h.tags,
        'one_night_charge': h.one_night_charge,
        'type': h.type
    })

@app.route('/api/hotels/<int:id>', methods=['DELETE'])
@login_required
def delete_hotel(id):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    hotel = Hotel.query.get_or_404(id)
    db.session.delete(hotel)
    db.session.commit()
    return jsonify({'message': 'Hotel deleted successfully!'})

@app.route('/api/hotels/delete-bulk', methods=['POST'])
@login_required
def delete_hotels_bulk():
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'error': 'No IDs provided'}), 400
    
    Hotel.query.filter(Hotel.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted {len(ids)} properties'})

import csv
import io
from flask import Response

@app.route('/admin/export/csv/<report_type>', methods=['GET'])
@login_required
def export_csv(report_type):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    
    si = io.StringIO()
    cw = csv.writer(si)
    
    if report_type == 'hotels':
        hotels = Hotel.query.order_by(Hotel.created_at.desc()).all()
        cw.writerow(['ID', 'Name', 'Category', 'Rating', 'Location', 'Price', 'Type', 'Status', 'Date Added'])
        for h in hotels:
            cw.writerow([h.id, h.name, h.category, h.rating, h.location, h.price, h.type, h.status, h.created_at.strftime('%Y-%m-%d')])
    elif report_type == 'users':
        users = User.query.all()
        cw.writerow(['ID', 'Username', 'Email', 'Role'])
        for u in users:
            cw.writerow([u.id, u.username, u.email, u.role])
    elif report_type == 'searches':
        searches = db.session.query(SearchHistory).order_by(SearchHistory.created_at.desc()).all()
        cw.writerow(['ID', 'User ID', 'Query', 'Timestamp'])
        for s in searches:
            cw.writerow([s.id, s.user_id, s.query, s.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    elif report_type == 'recommendations':
        # Mining semantic searches for recommendation trends
        searches = db.session.query(SearchHistory).all()
        search_queries = [s.query.lower() for s in searches]
        from collections import Counter
        top_searches = dict(Counter(search_queries).most_common(20))
        cw.writerow(['Semantic Keyword / Query', 'Frequency'])
        for k, v in top_searches.items():
            cw.writerow([k, v])
    elif report_type == 'partner_uploads':
        reqs = HotelRequest.query.order_by(HotelRequest.created_at.desc()).all()
        cw.writerow(['ID', 'Hotel Name', 'Category', 'Contact Email', 'Location', 'Status', 'Date Submitted'])
        for r in reqs:
            cw.writerow([r.id, r.name, r.category, r.contact_email, r.location, r.status, r.created_at.strftime('%Y-%m-%d')])
    else:
        return "Invalid report type", 400

    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename={report_type}_report.csv"})

@app.route('/admin/export/json/<report_type>', methods=['GET'])
@login_required
def export_json(report_type):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    
    if report_type == 'hotels':
        hotels = Hotel.query.order_by(Hotel.created_at.desc()).all()
        data = [[h.id, h.name, h.category, h.rating, h.location, h.price, h.type, h.status] for h in hotels]
        headers = ['ID', 'Name', 'Category', 'Rating', 'Location', 'Price', 'Type', 'Status']
        return jsonify({'headers': headers, 'data': data})
    elif report_type == 'users':
        users = User.query.all()
        data = [[u.id, u.username, u.email, u.role] for u in users]
        headers = ['ID', 'Username', 'Email', 'Role']
        return jsonify({'headers': headers, 'data': data})
    elif report_type == 'searches':
        searches = db.session.query(SearchHistory).order_by(SearchHistory.created_at.desc()).all()
        data = [[s.id, s.user_id, s.query, s.created_at.strftime('%Y-%m-%d')] for s in searches]
        headers = ['ID', 'User ID', 'Query', 'Date']
        return jsonify({'headers': headers, 'data': data})
    elif report_type == 'recommendations':
        searches = db.session.query(SearchHistory).all()
        search_queries = [s.query.lower() for s in searches]
        from collections import Counter
        top_searches = dict(Counter(search_queries).most_common(20))
        data = [[k, v] for k, v in top_searches.items()]
        headers = ['Semantic Keyword', 'Search Frequency']
        return jsonify({'headers': headers, 'data': data})
    elif report_type == 'partner_uploads':
        reqs = HotelRequest.query.order_by(HotelRequest.created_at.desc()).all()
        data = [[r.id, r.name, r.category, r.contact_email, r.status] for r in reqs]
        headers = ['ID', 'Hotel Name', 'Category', 'Contact Email', 'Status']
        return jsonify({'headers': headers, 'data': data})
    else:
        return jsonify({'error': 'Invalid report type'}), 400

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
