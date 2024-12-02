from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine, Base
from models import Transaction
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI()

# CORS middleware
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class TransactionSchema(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: datetime.date

    class Config:
        orm_mode = True


class TransactionModel(TransactionSchema):
    id: int


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database
Base.metadata.create_all(bind=engine)

# Routes
@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/", response_model=List[TransactionModel])
async def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions

@app.put("/transactions/{transaction_id}", response_model=TransactionModel)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionSchema,
    db: Session = Depends(get_db)
):
    # Cari transaksi berdasarkan ID
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update kolom berdasarkan input
    for key, value in transaction.dict().items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    # Cari transaksi berdasarkan ID
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(db_transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}
