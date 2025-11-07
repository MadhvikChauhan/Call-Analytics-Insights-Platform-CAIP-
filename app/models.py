
"""ORM models using SQLAlchemy declarative syntax (async-friendly).

Defines Company, CallRecord, and CallInsight models with relationships.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import Base

class SentimentEnum(str, enum.Enum):
    """Sentiment choices for call insights."""
    Positive = "Positive"
    Negative = "Negative"
    Neutral = "Neutral"

class Company(Base):
    """Represents a tenant/company in the CAIP system.

    Columns:
        id: Primary key
        name: Human-readable company name
        api_key: UUID string used to authenticate requests
        can_regen_reports: Permission flag for regenerating reports
    """
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    can_regen_reports = Column(Boolean, default=True, nullable=False)

    # relationship to calls
    calls = relationship("CallRecord", back_populates="company", cascade="all, delete-orphan")

class CallRecord(Base):
    """Stores metadata for a single call and path to the recording file."""
    __tablename__ = "callrecord"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), index=True, nullable=False)
    call_id = Column(String, unique=True, index=True, nullable=False)
    caller = Column(String, nullable=True)
    callee = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    recording_file = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="calls")
    insight = relationship("CallInsight", back_populates="call", uselist=False, cascade="all, delete-orphan")

class CallInsight(Base):
    """Stores processing results for a CallRecord (transcription, sentiment, etc.)."""
    __tablename__ = "callinsight"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("callrecord.id"), unique=True, nullable=False)
    transcription = Column(Text, nullable=True)
    sentiment = Column(Enum(SentimentEnum), nullable=True)
    keywords = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    call = relationship("CallRecord", back_populates="insight")
