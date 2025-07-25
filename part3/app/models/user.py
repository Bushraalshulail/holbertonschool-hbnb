# app/models/user.py

from app.extensions import db
from .base_model import BaseModel
from sqlalchemy.orm import relationship

class User(BaseModel):
    __tablename__ = 'users'
    _used_emails = set()

    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(128), nullable=False, unique=True)
    password   = db.Column(db.String(128), nullable=True)
    is_admin   = db.Column(db.Boolean, default=False, nullable=False)

    places = relationship("Place", back_populates="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="reviewer", cascade="all, delete-orphan")

    def __init__(self, first_name, last_name, email):
        if len(first_name) > 50:
            raise ValueError("first_name must be 50 characters or fewer")
        if len(last_name) > 50:
            raise ValueError("last_name must be 50 characters or fewer")
        if not email or not email.strip():
            raise ValueError("Email is required")
        if '@' not in email:
            raise ValueError("Invalid email format")
        if email in User._used_emails:
            raise ValueError("email must be unique")
        super().__init__()
        self.first_name = first_name
        self.last_name  = last_name
        self.email      = email
        User._used_emails.add(email)
