from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False)
    taxpayer_id = Column(String, index=True, nullable=False)
    business_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    account = relationship("Account", back_populates="businesses")
    invoices = relationship("Invoice", back_populates="business", cascade="all, delete-orphan")
    statistics = relationship("StampingStatistics", back_populates="business", cascade="all, delete-orphan")
    batches = relationship("StampingBatch", back_populates="business", cascade="all, delete-orphan")