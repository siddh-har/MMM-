from app import app, db, User

with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"Admin found: {admin.username}")
    else:
        print("No admin found")
