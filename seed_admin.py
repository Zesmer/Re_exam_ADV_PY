# seed_admin.py (in project root)
from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Create admin user
db = SessionLocal()

# Check if admin exists
admin_exists = db.query(User).filter(User.email == "admin@example.com").first()

if not admin_exists:
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="System Admin",
        is_admin=True,
        phone="+1234567890",
        address="Admin Office"
    )
    db.add(admin_user)
    db.commit()
    print("✅ Admin user created successfully!")
    print("📧 Email: admin@example.com")
    print("🔑 Password: admin123")
else:
    print("⚠️ Admin user already exists")

db.close()