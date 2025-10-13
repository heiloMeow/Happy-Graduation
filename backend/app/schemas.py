"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class UserCreate(BaseModel):
    """User creation schema."""
    session_id: str
    nickname: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema."""
    avatar_color: Optional[str] = None
    avatar_status: Optional[str] = None
    nickname: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    session_id: str
    avatar_color: Optional[str] = None
    avatar_status: Optional[str] = None
    nickname: Optional[str] = None

    class Config:
        from_attributes = True


class SeatStatus(BaseModel):
    """Seat status schema."""
    number: int
    occupied: bool
    current_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class SeatOccupy(BaseModel):
    """Seat occupation request."""
    user_id: int


class SignalCreate(BaseModel):
    """Signal creation schema."""
    user_id: int
    text: str
    position: str


class SignalResponse(BaseModel):
    """Signal response schema."""
    id: int
    user_id: int
    text: str
    position: str

    class Config:
        from_attributes = True


class TableMemberInfo(BaseModel):
    """Table member info."""
    user_id: int
    nickname: Optional[str] = None
    avatar_color: Optional[str] = None
    avatar_status: Optional[str] = None
    signals: List[SignalResponse] = []
    table_number: Optional[int] = None
    seat_number: Optional[int] = None

    class Config:
        from_attributes = True


class TableResponse(BaseModel):
    """Table response schema."""
    id: int
    number: int
    members: List[TableMemberInfo] = []

    class Config:
        from_attributes = True


class TableNearby(BaseModel):
    """Nearby table info."""
    id: int
    number: int
    members: List[TableMemberInfo] = []

    class Config:
        from_attributes = True


class MessageSend(BaseModel):
    """Message send request."""
    from_table_id: int
    to_table_id: int
    to_user_id: Optional[int] = None  # If specified, send to specific user
    content: str


class MessageReply(BaseModel):
    """Message reply request."""
    reply: str
    replier_user_id: Optional[int] = None


class MessageResponse(BaseModel):
    """Message response schema."""
    id: int
    from_table_id: int
    to_table_id: int
    content: str
    reply: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class WSMessage(BaseModel):
    """WebSocket message schema."""
    type: str
    data: dict

