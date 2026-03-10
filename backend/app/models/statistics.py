from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class StampingStatistics(Base):
    __tablename__ = "stamping_statistics"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    period = Column(String, nullable=False)
    total_invoices = Column(Integer, default=0)
    stamped_success = Column(Integer, default=0)
    stamped_error = Column(Integer, default=0)
    validation_errors = Column(Integer, default=0)
    certificate_errors = Column(Integer, default=0)
    pac_errors = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.datetime.utcnow)

    business = relationship("Business", back_populates="statistics")