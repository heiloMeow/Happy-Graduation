"""SQLAlchemy models for NudgeeQ."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ReplyType(str, enum.Enum):
    """Message reply types."""
    SORRY = "SORRY"
    IGNORE = "IGNORE"
    SURE = "SURE"


class User(Base):
    """User model for anonymous session-based users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    avatar_color = Column(String, nullable=True)
    avatar_status = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    signals = relationship("Signal", back_populates="user", cascade="all, delete-orphan")
    table_memberships = relationship("TableMember", back_populates="user", cascade="all, delete-orphan")
    occupied_seat = relationship("Seat", back_populates="current_user", uselist=False)


class Seat(Base):
    """Seat model for 4 available seats."""
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False)
    occupied = Column(Boolean, default=False)
    current_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    current_user = relationship("User", back_populates="occupied_seat")


class Table(Base):
    """Table model representing shared workspaces."""
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("TableMember", back_populates="table", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="[Message.from_table_id]", back_populates="from_table")
    received_messages = relationship("Message", foreign_keys="[Message.to_table_id]", back_populates="to_table")


class TableMember(Base):
    """Association table for table members."""
    __tablename__ = "table_members"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    table = relationship("Table", back_populates="members")
    user = relationship("User", back_populates="table_memberships")


class Signal(Base):
    """Signal model for user status bubbles."""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    position = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="signals")


class Message(Base):
    """Message model for cross-table communication."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    from_table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    to_table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    content = Column(String, nullable=False)
    reply = Column(Enum(ReplyType), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    from_table = relationship("Table", foreign_keys=[from_table_id], back_populates="sent_messages")
    to_table = relationship("Table", foreign_keys=[to_table_id], back_populates="received_messages")

