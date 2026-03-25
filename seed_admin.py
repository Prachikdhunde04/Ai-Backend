from database import SessionLocal, engine, Base
import models
from core.security import get_password_hash

def seed_admin():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    admin_email = "admin@company.com"
    existing_admin = db.query(models.User).filter(models.User.email == admin_email).first()
    if not existing_admin:
        hashed_password = get_password_hash("Admin@123")
        admin_user = models.User(
            email=admin_email,
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user seeded: {admin_email} / Admin@123")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    seed_admin()
