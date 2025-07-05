from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_bud.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default="001")
    name = Column(String, default="Default User")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    categories = relationship("Category", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    budget_plans = relationship("BudgetPlan", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), default="001")
    name = Column(String, index=True)
    color = Column(String, default="#3B82F6")
    budget_limit = Column(Float, default=0.0)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), default="001")
    date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    confidence_score = Column(Float, default=0.0)
    file_source = Column(String)
    needs_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class BudgetPlan(Base):
    __tablename__ = "budget_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), default="001")
    income = Column(Float)
    needs_pct = Column(Float, default=50.0)
    wants_pct = Column(Float, default=30.0)
    savings_pct = Column(Float, default=20.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="budget_plans")

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_data():
    """Initialize default user and categories"""
    db = SessionLocal()
    try:
        # Create default user
        user = db.query(User).filter(User.id == "001").first()
        if not user:
            user = User(id="001", name="Default User")
            db.add(user)
        
        # Create default categories
        default_categories = [
            {"name": "Groceries", "color": "#10B981"},
            {"name": "Dining", "color": "#F59E0B"},
            {"name": "Transportation", "color": "#3B82F6"},
            {"name": "Bills", "color": "#EF4444"},
            {"name": "Entertainment", "color": "#8B5CF6"},
            {"name": "Shopping", "color": "#EC4899"},
            {"name": "Healthcare", "color": "#06B6D4"},
            {"name": "Other", "color": "#6B7280"},
        ]
        
        for cat_data in default_categories:
            existing = db.query(Category).filter(
                Category.user_id == "001",
                Category.name == cat_data["name"]
            ).first()
            if not existing:
                category = Category(
                    user_id="001",
                    name=cat_data["name"],
                    color=cat_data["color"],
                    is_custom=False
                )
                db.add(category)
        
        db.commit()
    finally:
        db.close()
