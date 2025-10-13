"""Seat management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Seat, User, Table, TableMember, Signal
from app.schemas import SeatStatus, SeatOccupy, TableMemberInfo
from app.routers.ws import manager

router = APIRouter(prefix="/api/seats", tags=["seats"])


def _ensure_tables_exist(db: Session):
    """Ensure Table 1 and Table 2 exist."""
    table1 = db.query(Table).filter(Table.number == 1).first()
    if not table1:
        table1 = Table(number=1)
        db.add(table1)
    
    table2 = db.query(Table).filter(Table.number == 2).first()
    if not table2:
        table2 = Table(number=2)
        db.add(table2)
    
    db.commit()
    return table1, table2


@router.get("/status", response_model=list[SeatStatus])
def get_seats_status(db: Session = Depends(get_db)):
    """Get all seats status (8 seats for 2 tables)."""
    _ensure_tables_exist(db)
    
    seats = db.query(Seat).order_by(Seat.number).all()
    if not seats:
        for i in range(1, 9):
            seat = Seat(number=i, occupied=False)
            db.add(seat)
        db.commit()
        seats = db.query(Seat).order_by(Seat.number).all()
    return seats


@router.post("/{seat_num}/occupy")
async def occupy_seat(seat_num: int, occupy: SeatOccupy, db: Session = Depends(get_db)):
    """Occupy a seat and auto-join corresponding table."""
    if seat_num < 1 or seat_num > 8:
        raise HTTPException(status_code=400, detail="Invalid seat number")
    
    _ensure_tables_exist(db)
    
    seat = db.query(Seat).filter(Seat.number == seat_num).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    
    if seat.occupied and seat.current_user_id != occupy.user_id:
        raise HTTPException(status_code=409, detail="Seat already occupied")
    
    user = db.query(User).filter(User.id == occupy.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Determine table number based on seat number (1-4 -> Table 1, 5-8 -> Table 2)
    table_number = 1 if seat_num <= 4 else 2
    target_table = db.query(Table).filter(Table.number == table_number).first()
    
    if not target_table:
        raise HTTPException(status_code=500, detail="Table not found")
    
    # Check table capacity (max 4 per table)
    current_members = db.query(TableMember).filter(TableMember.table_id == target_table.id).count()
    if current_members >= 4:
        # Check if user is already member
        existing = db.query(TableMember).filter(
            TableMember.table_id == target_table.id,
            TableMember.user_id == occupy.user_id
        ).first()
        if not existing:
            raise HTTPException(status_code=409, detail="Table is full")
    
    # Release old seat if exists
    old_seat = db.query(Seat).filter(Seat.current_user_id == occupy.user_id).first()
    if old_seat:
        old_seat.occupied = False
        old_seat.current_user_id = None
    
    # Remove from old table if exists
    old_membership = db.query(TableMember).filter(TableMember.user_id == occupy.user_id).first()
    if old_membership:
        db.delete(old_membership)
    
    # Occupy new seat
    seat.occupied = True
    seat.current_user_id = occupy.user_id
    
    # Join new table
    new_membership = TableMember(table_id=target_table.id, user_id=occupy.user_id)
    db.add(new_membership)
    
    db.commit()
    db.refresh(target_table)
    
    # Broadcast table update to all members
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
    
    return {"success": True, "seat_number": seat_num, "table_number": table_number}


@router.post("/{seat_num}/release")
def release_seat(seat_num: int, db: Session = Depends(get_db)):
    """Release a seat."""
    seat = db.query(Seat).filter(Seat.number == seat_num).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    
    seat.occupied = False
    seat.current_user_id = None
    db.commit()
    
    return {"success": True, "seat_number": seat_num}

