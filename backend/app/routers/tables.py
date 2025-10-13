"""Table management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Table, TableMember, User, Signal, Seat
from app.schemas import TableResponse, TableMemberInfo, TableNearby
from app.routers.ws import manager

router = APIRouter(prefix="/api/tables", tags=["tables"])


def _create_table_member_info(user: User, table: Table, db: Session) -> TableMemberInfo:
    """Helper to create TableMemberInfo with seat and table info."""
    signals = db.query(Signal).filter(Signal.user_id == user.id).all()
    seat = db.query(Seat).filter(Seat.current_user_id == user.id).first()
    seat_number = seat.number if seat else None
    
    return TableMemberInfo(
        user_id=user.id,
        nickname=user.nickname,
        avatar_color=user.avatar_color,
        avatar_status=user.avatar_status,
        signals=[s for s in signals],
        table_number=table.number if table else None,
        seat_number=seat_number
    )


def _get_table_with_members(table: Table, db: Session) -> dict:
    """Helper to format table with members."""
    members_info = []
    for tm in table.members:
        member_info = _create_table_member_info(tm.user, table, db)
        members_info.append(member_info)
    
    return {
        "id": table.id,
        "number": table.number,
        "members": members_info
    }


@router.post("/join", response_model=TableResponse)
async def join_table(user_id: int, table_number: int = None, db: Session = Depends(get_db)):
    """Join a table (only Table 1 or Table 2)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ensure tables exist
    table1 = db.query(Table).filter(Table.number == 1).first()
    if not table1:
        table1 = Table(number=1)
        db.add(table1)
    
    table2 = db.query(Table).filter(Table.number == 2).first()
    if not table2:
        table2 = Table(number=2)
        db.add(table2)
    
    db.commit()
    
    existing_membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if existing_membership:
        table = existing_membership.table
        return _get_table_with_members(table, db)
    
    # Determine which table to join
    if table_number:
        if table_number not in [1, 2]:
            raise HTTPException(status_code=400, detail="Only Table 1 and Table 2 are available")
        table = db.query(Table).filter(Table.number == table_number).first()
    else:
        # Auto-assign to table with space
        table1_count = db.query(TableMember).filter(TableMember.table_id == table1.id).count()
        table2_count = db.query(TableMember).filter(TableMember.table_id == table2.id).count()
        
        if table1_count < 4:
            table = table1
        elif table2_count < 4:
            table = table2
        else:
            raise HTTPException(status_code=409, detail="Both tables are full")
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Check capacity
    member_count = db.query(TableMember).filter(TableMember.table_id == table.id).count()
    if member_count >= 4:
        raise HTTPException(status_code=409, detail="Table is full")
    
    membership = TableMember(table_id=table.id, user_id=user_id)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    # Refresh table to get updated members
    db.refresh(table)
    result = _get_table_with_members(table, db)
    
    # Get all member IDs including the new one
    member_ids = [m.user_id for m in table.members]
    await manager.broadcast_to_table(
        table.id,
        member_ids,
        {"type": "table_update", "data": result}
    )
    
    return result


@router.get("/nearby", response_model=list[TableNearby])
def get_nearby_tables(keyword: str = None, exclude_table_id: int = None, db: Session = Depends(get_db)):
    """Get all tables with members, optionally filtered by keyword.
    
    Note: exclude_table_id is kept for API compatibility but not used.
    All tables are shown to reduce social anxiety - users can see themselves in the list.
    """
    tables = db.query(Table).all()
    
    results = []
    for table in tables:
        members_info = []
        for tm in table.members:
            user = tm.user
            
            if keyword:
                signals_temp = db.query(Signal).filter(Signal.user_id == user.id).all()
                has_keyword = any(keyword.lower() in s.text.lower() for s in signals_temp)
                if not has_keyword:
                    continue
            
            member_info = _create_table_member_info(user, table, db)
            members_info.append(member_info)
        
        # Only add table if it has members
        # (when keyword is specified, members_info only contains matching members)
        if members_info:
            results.append(TableNearby(
                id=table.id,
                number=table.number,
                members=members_info
            ))
    
    return results


@router.get("/user/{user_id}", response_model=TableResponse)
def get_user_table(user_id: int, db: Session = Depends(get_db)):
    """Get the table a user is currently at."""
    membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="User not in any table")
    
    table = membership.table
    return _get_table_with_members(table, db)


@router.get("/{table_id}", response_model=TableResponse)
def get_table_by_id(table_id: int, db: Session = Depends(get_db)):
    """Get a specific table by ID with all members."""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    return _get_table_with_members(table, db)


@router.post("/leave")
async def leave_table(user_id: int, db: Session = Depends(get_db)):
    """Leave current table."""
    membership = db.query(TableMember).filter(TableMember.user_id == user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="User not in any table")
    
    table = membership.table
    table_id = table.id
    
    db.delete(membership)
    db.commit()
    
    remaining = db.query(TableMember).filter(TableMember.table_id == table_id).all()
    if not remaining:
        db.delete(table)
        db.commit()
    else:
        result = _get_table_with_members(table, db)
        member_ids = [m.user_id for m in remaining]
        await manager.broadcast_to_table(
            table_id,
            member_ids,
            {"type": "table_update", "data": result}
        )
    
    return {"success": True}

