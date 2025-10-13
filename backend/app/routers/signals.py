"""Signal management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Signal, User, TableMember, Table
from app.schemas import SignalCreate, SignalResponse, TableMemberInfo
from app.routers.ws import manager

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.post("/", response_model=SignalResponse)
async def create_signal(signal: SignalCreate, db: Session = Depends(get_db)):
    """Create a signal."""
    user = db.query(User).filter(User.id == signal.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_signal = Signal(
        user_id=signal.user_id,
        text=signal.text,
        position=signal.position
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    
    # Broadcast table update if user is in a table
    membership = db.query(TableMember).filter(TableMember.user_id == signal.user_id).first()
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
    
    return db_signal


@router.get("/user/{user_id}", response_model=list[SignalResponse])
def get_user_signals(user_id: int, db: Session = Depends(get_db)):
    """Get all signals for a user."""
    signals = db.query(Signal).filter(Signal.user_id == user_id).all()
    return signals


@router.delete("/{signal_id}")
async def delete_signal(signal_id: int, db: Session = Depends(get_db)):
    """Delete a signal."""
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
    
    return {"success": True}


@router.delete("/user/{user_id}/all")
async def delete_all_user_signals(user_id: int, db: Session = Depends(get_db)):
    """Delete all signals for a user."""
    db.query(Signal).filter(Signal.user_id == user_id).delete()
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
    
    return {"success": True}

