from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class ErrorStamping(Base):
    __tablename__ = "errors_stamping"

    id = Column(Integer, primary_key=True, index=True)
    buffer_id = Column(Integer, ForeignKey("buffer.id", ondelete="CASCADE"), nullable=False)
    invoice_uuid = Column(String, ForeignKey("invoices.uuid", ondelete="CASCADE"), nullable=True)
    response_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=False)
    error_stage = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    buffer = relationship("Buffer", back_populates="errors")
    invoice = relationship("Invoice", back_populates="errors")