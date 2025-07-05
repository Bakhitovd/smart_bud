from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import os

from .database import get_db, create_tables, init_default_data, User, Category, Transaction
from .services.file_processor import FileProcessor
from .services.categorizer import TransactionCategorizer

app = FastAPI(title="Smart Budget Companion", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
file_processor = FileProcessor()
categorizer = TransactionCategorizer()

@app.on_event("startup")
async def startup_event():
    """Initialize database and default data on startup"""
    create_tables()
    init_default_data()

@app.get("/")
async def root():
    return {"message": "Smart Budget Companion API", "status": "running"}

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a financial statement file
    """
    try:
        # Read file content
        content = await file.read()
        file_content = content.decode('utf-8')
        
        # Extract transactions using LLM
        extracted_transactions = await file_processor.extract_transactions(
            file_content, file.filename
        )
        
        if not extracted_transactions:
            return {
                "success": False,
                "message": "No transactions found in the file",
                "transactions_processed": 0
            }
        
        # Get available categories
        categories = db.query(Category).filter(Category.user_id == "001").all()
        category_data = [{"id": cat.id, "name": cat.name} for cat in categories]
        
        # Categorize transactions using LLM
        categorized_transactions = await categorizer.categorize_batch(
            extracted_transactions, category_data
        )
        
        # Save transactions to database
        saved_transactions = []
        for trans_data in categorized_transactions:
            # Get category ID
            category_id = categorizer.get_category_id_by_name(
                trans_data["category_name"], category_data
            )
            
            # Parse date
            try:
                transaction_date = datetime.fromisoformat(trans_data["date"].replace('Z', '+00:00'))
            except:
                transaction_date = datetime.now()
            
            # Create transaction record
            transaction = Transaction(
                user_id="001",
                date=transaction_date,
                amount=trans_data["amount"],
                description=trans_data["description"],
                category_id=category_id,
                confidence_score=trans_data["confidence_score"],
                file_source=file.filename,
                needs_review=trans_data["needs_review"]
            )
            
            db.add(transaction)
            saved_transactions.append({
                "description": trans_data["description"],
                "amount": trans_data["amount"],
                "category": trans_data["category_name"],
                "confidence": trans_data["confidence_score"],
                "needs_review": trans_data["needs_review"]
            })
        
        db.commit()
        
        # Count transactions needing review
        review_count = sum(1 for t in saved_transactions if t["needs_review"])
        
        return {
            "success": True,
            "message": f"Successfully processed {len(saved_transactions)} transactions",
            "transactions_processed": len(saved_transactions),
            "needs_review": review_count,
            "transactions": saved_transactions[:10]  # Return first 10 for preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/transactions")
async def get_transactions(
    limit: int = 100,
    needs_review: bool = None,
    db: Session = Depends(get_db)
):
    """
    Get transactions with optional filtering
    """
    query = db.query(Transaction).filter(Transaction.user_id == "001")
    
    if needs_review is not None:
        query = query.filter(Transaction.needs_review == needs_review)
    
    transactions = query.order_by(Transaction.date.desc()).limit(limit).all()
    
    result = []
    for trans in transactions:
        result.append({
            "id": trans.id,
            "date": trans.date.isoformat(),
            "amount": trans.amount,
            "description": trans.description,
            "category": trans.category.name if trans.category else "Uncategorized",
            "category_id": trans.category_id,
            "confidence_score": trans.confidence_score,
            "needs_review": trans.needs_review,
            "file_source": trans.file_source
        })
    
    return {
        "transactions": result,
        "total": len(result)
    }

@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """
    Get all categories for the user
    """
    categories = db.query(Category).filter(Category.user_id == "001").all()
    
    result = []
    for cat in categories:
        result.append({
            "id": cat.id,
            "name": cat.name,
            "color": cat.color,
            "budget_limit": cat.budget_limit,
            "is_custom": cat.is_custom
        })
    
    return {"categories": result}

@app.get("/api/review-queue")
async def get_review_queue(db: Session = Depends(get_db)):
    """
    Get transactions that need manual review
    """
    transactions = db.query(Transaction).filter(
        Transaction.user_id == "001",
        Transaction.needs_review == True
    ).order_by(Transaction.date.desc()).all()
    
    result = []
    for trans in transactions:
        result.append({
            "id": trans.id,
            "date": trans.date.isoformat(),
            "amount": trans.amount,
            "description": trans.description,
            "category": trans.category.name if trans.category else "Uncategorized",
            "confidence_score": trans.confidence_score
        })
    
    return {
        "transactions": result,
        "count": len(result)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
