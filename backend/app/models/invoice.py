from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    buffer_id = Column(Integer, ForeignKey("buffer.id", ondelete="SET NULL"), nullable=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    response_code = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    taxpayer_id = Column(String, index=True, nullable=False)
    rtaxpayer_id = Column(String, nullable=True)
    total = Column(Numeric(12, 2), nullable=False)
    xml_timbrado = Column(Text, nullable=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.datetime.utcnow)

    buffer = relationship("Buffer", back_populates="invoices")
    business = relationship("Business", back_populates="invoices")
    errors = relationship("ErrorStamping", back_populates="invoice", cascade="all, delete-orphan")