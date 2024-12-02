from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, Date

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)
    is_income = Column(Boolean, default=False)
    date = Column(Date, nullable=False)
