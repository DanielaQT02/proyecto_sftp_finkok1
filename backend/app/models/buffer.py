from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Buffer(Base):
    __tablename__ = "buffer"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("stamping_batches.id", ondelete="SET NULL"), nullable=True)
    xml_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.datetime.utcnow)

    batch = relationship("StampingBatch", back_populates="buffers")
    invoices = relationship("Invoice", back_populates="buffer", cascade="all, delete-orphan")
    errors = relationship("ErrorStamping", back_populates="buffer", cascade="all, delete-orphan")