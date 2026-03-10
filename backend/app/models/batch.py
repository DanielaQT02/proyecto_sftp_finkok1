from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class StampingBatch(Base):
    __tablename__ = "stamping_batches"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    zip_name = Column(String, nullable=False)
    total_xml = Column(Integer, default=0)
    task_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.datetime.utcnow)

    business = relationship("Business", back_populates="batches")
    buffers = relationship("Buffer", back_populates="batch", cascade="all, delete-orphan")