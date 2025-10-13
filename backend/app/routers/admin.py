"""Admin routes for testing and debugging."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Seat, Table, TableMember, Signal, Message
from app.routers.ws import manager
from app.schemas import TableMemberInfo

router = APIRouter(prefix="/api/admin", tags=["admin"])


class AdminUserCreate(BaseModel):
    """Admin user creation schema."""
    nickname: str
    avatar_color: Optional[str] = None
    avatar_status: Optional[str] = None


class AdminUserUpdate(BaseModel):
    """Admin user update schema."""
    nickname: Optional[str] = None
    avatar_color: Optional[str] = None
    avatar_status: Optional[str] = None


class AdminSignalCreate(BaseModel):
    """Admin signal creation schema."""
    text: str
    position: str  # "left" or "right"


@router.get("/users")
def get_all_users(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all users with their status."""
    users = db.query(User).all()
    result = []
    
    for user in users:
        seat = db.query(Seat).filter(Seat.current_user_id == user.id).first()
        membership = db.query(TableMember).filter(TableMember.user_id == user.id).first()
        signals = db.query(Signal).filter(Signal.user_id == user.id).all()
        
        result.append({
            "id": user.id,
            "session_id": user.session_id,
            "nickname": user.nickname,
            "avatar_color": user.avatar_color,
            "avatar_status": user.avatar_status,
            "seat_number": seat.number if seat else None,
            "table_number": membership.table.number if membership else None,
            "signals_count": len(signals),
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return result


@router.get("/tables")
def get_all_tables(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all tables with member info."""
    tables = db.query(Table).all()
    result = []
    
    for table in tables:
        members = db.query(TableMember).filter(TableMember.table_id == table.id).all()
        member_info = []
        
        for tm in members:
            user = tm.user
            seat = db.query(Seat).filter(Seat.current_user_id == user.id).first()
            member_info.append({
                "user_id": user.id,
                "nickname": user.nickname,
                "seat_number": seat.number if seat else None,
                "avatar_color": user.avatar_color,
                "avatar_status": user.avatar_status
            })
        
        result.append({
            "id": table.id,
            "number": table.number,
            "members_count": len(members),
            "members": member_info,
            "created_at": table.created_at.isoformat() if table.created_at else None
        })
    
    return result


@router.post("/kick/{user_id}")
async def kick_user(user_id: int, db: Session = Depends(get_db)):
    """Kick a user (release seat, remove from table, delete signals)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get table before removing user
    membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    old_table_id = membership.table_id if membership else None
    
    # Release seat
    seat = db.query(Seat).filter(Seat.current_user_id == user_id).first()
    if seat:
        seat.occupied = False
        seat.current_user_id = None
    
    # Remove from table
    if membership:
        db.delete(membership)
    
    # Delete signals
    signals = db.query(Signal).filter(Signal.user_id == user_id).all()
    for signal in signals:
        db.delete(signal)
    
    # Delete user
    db.delete(user)
    db.commit()
    
    # Broadcast table update to remaining members
    if old_table_id:
        old_table = db.query(Table).filter(Table.id == old_table_id).first()
        if old_table:
            members_info = []
            for tm in old_table.members:
                member_user = tm.user
                signals = db.query(Signal).filter(Signal.user_id == member_user.id).all()
                member_info = TableMemberInfo(
                    user_id=member_user.id,
                    nickname=member_user.nickname,
                    avatar_color=member_user.avatar_color,
                    avatar_status=member_user.avatar_status,
                    signals=[s for s in signals]
                )
                members_info.append(member_info)
            
            member_ids = [tm.user_id for tm in old_table.members]
            await manager.broadcast_to_table(
                old_table.id,
                member_ids,
                {
                    "type": "table_update",
                    "data": {
                        "id": old_table.id,
                        "number": old_table.number,
                        "members": [m.model_dump() for m in members_info]
                    }
                }
            )
    
    return {"success": True, "message": f"User {user_id} kicked"}


@router.post("/reset")
def reset_database(db: Session = Depends(get_db)):
    """Reset all data (for testing only)."""
    # Delete all messages
    db.query(Message).delete()
    
    # Delete all signals
    db.query(Signal).delete()
    
    # Delete all table members
    db.query(TableMember).delete()
    
    # Reset all seats
    seats = db.query(Seat).all()
    for seat in seats:
        seat.occupied = False
        seat.current_user_id = None
    
    # Delete all users
    db.query(User).delete()
    
    # Keep tables but clean them
    # Don't delete Table 1 and Table 2
    
    db.commit()
    
    return {"success": True, "message": "Database reset completed"}


@router.get("/seats")
def get_all_seats(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all seats status."""
    seats = db.query(Seat).order_by(Seat.number).all()
    result = []
    
    for seat in seats:
        user = None
        if seat.current_user_id:
            user = db.query(User).filter(User.id == seat.current_user_id).first()
        
        result.append({
            "number": seat.number,
            "occupied": seat.occupied,
            "user_id": seat.current_user_id,
            "user_nickname": user.nickname if user else None
        })
    
    return result


@router.post("/users")
def create_user_admin(user_data: AdminUserCreate, db: Session = Depends(get_db)):
    """Create a new user (admin)."""
    import uuid
    session_id = f"admin_{uuid.uuid4().hex[:16]}"
    
    new_user = User(
        session_id=session_id,
        nickname=user_data.nickname,
        avatar_color=user_data.avatar_color,
        avatar_status=user_data.avatar_status
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "session_id": new_user.session_id,
        "nickname": new_user.nickname,
        "avatar_color": new_user.avatar_color,
        "avatar_status": new_user.avatar_status
    }


@router.put("/users/{user_id}")
async def update_user_admin(user_id: int, user_data: AdminUserUpdate, db: Session = Depends(get_db)):
    """Update user (admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.nickname is not None:
        user.nickname = user_data.nickname
    if user_data.avatar_color is not None:
        user.avatar_color = user_data.avatar_color
    if user_data.avatar_status is not None:
        user.avatar_status = user_data.avatar_status
    
    db.commit()
    db.refresh(user)
    
    # Broadcast table update if user is in a table
    membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if membership:
        table = membership.table
        members_info = []
        for tm in table.members:
            member_user = tm.user
            signals = db.query(Signal).filter(Signal.user_id == member_user.id).all()
            member_info = TableMemberInfo(
                user_id=member_user.id,
                nickname=member_user.nickname,
                avatar_color=member_user.avatar_color,
                avatar_status=member_user.avatar_status,
                signals=[s for s in signals]
            )
            members_info.append(member_info)
        
        member_ids = [tm.user_id for tm in table.members]
        await manager.broadcast_to_table(
            table.id,
            member_ids,
            {
                "type": "table_update",
                "data": {
                    "id": table.id,
                    "number": table.number,
                    "members": [m.model_dump() for m in members_info]
                }
            }
        )
    
    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar_color": user.avatar_color,
        "avatar_status": user.avatar_status
    }


@router.post("/seats/{seat_number}/assign/{user_id}")
async def assign_seat_admin(seat_number: int, user_id: int, db: Session = Depends(get_db)):
    """Assign a seat to a user (admin)."""
    if seat_number < 1 or seat_number > 8:
        raise HTTPException(status_code=400, detail="Invalid seat number")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    seat = db.query(Seat).filter(Seat.number == seat_number).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    
    # Release old seat
    old_seat = db.query(Seat).filter(Seat.current_user_id == user_id).first()
    old_table_id = None
    if old_seat:
        old_seat.occupied = False
        old_seat.current_user_id = None
    
    # Remove from old table
    old_membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if old_membership:
        old_table_id = old_membership.table_id
        db.delete(old_membership)
    
    # Assign new seat
    if seat.occupied and seat.current_user_id != user_id:
        raise HTTPException(status_code=409, detail="Seat is occupied")
    
    seat.occupied = True
    seat.current_user_id = user_id
    
    # Auto-join table
    table_number = 1 if seat_number <= 4 else 2
    target_table = db.query(Table).filter(Table.number == table_number).first()
    
    if target_table:
        new_membership = TableMember(table_id=target_table.id, user_id=user_id)
        db.add(new_membership)
    
    db.commit()
    db.refresh(target_table)
    
    # Broadcast table update to all members of the new table
    if target_table:
        members_info = []
        for tm in target_table.members:
            member_user = tm.user
            signals = db.query(Signal).filter(Signal.user_id == member_user.id).all()
            member_info = TableMemberInfo(
                user_id=member_user.id,
                nickname=member_user.nickname,
                avatar_color=member_user.avatar_color,
                avatar_status=member_user.avatar_status,
                signals=[s for s in signals]
            )
            members_info.append(member_info)
        
        member_ids = [tm.user_id for tm in target_table.members]
        await manager.broadcast_to_table(
            target_table.id,
            member_ids,
            {
                "type": "table_update",
                "data": {
                    "id": target_table.id,
                    "number": target_table.number,
                    "members": [m.model_dump() for m in members_info]
                }
            }
        )
    
    # Also broadcast to old table if user was moved
    if old_table_id and old_table_id != target_table.id:
        old_table = db.query(Table).filter(Table.id == old_table_id).first()
        if old_table:
            old_members_info = []
            for tm in old_table.members:
                member_user = tm.user
                signals = db.query(Signal).filter(Signal.user_id == member_user.id).all()
                member_info = TableMemberInfo(
                    user_id=member_user.id,
                    nickname=member_user.nickname,
                    avatar_color=member_user.avatar_color,
                    avatar_status=member_user.avatar_status,
                    signals=[s for s in signals]
                )
                old_members_info.append(member_info)
            
            old_member_ids = [tm.user_id for tm in old_table.members]
            await manager.broadcast_to_table(
                old_table.id,
                old_member_ids,
                {
                    "type": "table_update",
                    "data": {
                        "id": old_table.id,
                        "number": old_table.number,
                        "members": [m.model_dump() for m in old_members_info]
                    }
                }
            )
    
    return {"success": True, "seat_number": seat_number, "table_number": table_number}


@router.post("/users/{user_id}/signals")
async def add_signal_to_user(user_id: int, signal_data: AdminSignalCreate, db: Session = Depends(get_db)):
    """Add a signal to user (admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if signal_data.position not in ["left", "right"]:
        raise HTTPException(status_code=400, detail="Position must be 'left' or 'right'")
    
    new_signal = Signal(
        user_id=user_id,
        text=signal_data.text,
        position=signal_data.position
    )
    db.add(new_signal)
    db.commit()
    db.refresh(new_signal)
    
    # Broadcast table update if user is in a table
    membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if membership:
        table = membership.table
        members_info = []
        for tm in table.members:
            member_user = tm.user
            signals = db.query(Signal).filter(Signal.user_id == member_user.id).all()
            member_info = TableMemberInfo(
                user_id=member_user.id,
                nickname=member_user.nickname,
                avatar_color=member_user.avatar_color,
                avatar_status=member_user.avatar_status,
                signals=[s for s in signals]
            )
            members_info.append(member_info)
        
        member_ids = [tm.user_id for tm in table.members]
        await manager.broadcast_to_table(
            table.id,
            member_ids,
            {
                "type": "table_update",
                "data": {
                    "id": table.id,
                    "number": table.number,
                    "members": [m.model_dump() for m in members_info]
                }
            }
        )
    
    return {
        "id": new_signal.id,
        "user_id": new_signal.user_id,
        "text": new_signal.text,
        "position": new_signal.position
    }


@router.delete("/signals/{signal_id}")
async def delete_signal_admin(signal_id: int, db: Session = Depends(get_db)):
    """Delete a signal (admin)."""
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    user_id = signal.user_id
    db.delete(signal)
    db.commit()
    
    # Broadcast table update if user is in a table
    membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if membership:
        table = membership.table
        members_info = []
        for tm in table.members:
            member_user = tm.user
            signals = db.query(Signal).filter(Signal.user_id == member_user.id).all()
            member_info = TableMemberInfo(
                user_id=member_user.id,
                nickname=member_user.nickname,
                avatar_color=member_user.avatar_color,
                avatar_status=member_user.avatar_status,
                signals=[s for s in signals]
            )
            members_info.append(member_info)
        
        member_ids = [tm.user_id for tm in table.members]
        await manager.broadcast_to_table(
            table.id,
            member_ids,
            {
                "type": "table_update",
                "data": {
                    "id": table.id,
                    "number": table.number,
                    "members": [m.model_dump() for m in members_info]
                }
            }
        )
    
    return {"success": True, "message": f"Signal {signal_id} deleted"}


@router.get("/users/{user_id}/signals")
def get_user_signals(user_id: int, db: Session = Depends(get_db)):
    """Get all signals for a user (admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    signals = db.query(Signal).filter(Signal.user_id == user_id).all()
    
    return [
        {
            "id": s.id,
            "text": s.text,
            "position": s.position
        }
        for s in signals
    ]

