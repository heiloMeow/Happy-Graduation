"""User management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, TableMember, Signal
from app.schemas import UserCreate, UserUpdate, UserResponse, TableMemberInfo
from app.routers.ws import manager

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create or get existing user by session_id."""
    existing = db.query(User).filter(User.session_id == user.session_id).first()
    if existing:
        return existing
    
    db_user = User(session_id=user.session_id, nickname=user.nickname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user status and avatar."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.avatar_color is not None:
        user.avatar_color = user_update.avatar_color
    if user_update.avatar_status is not None:
        user.avatar_status = user_update.avatar_status
    if user_update.nickname is not None:
        user.nickname = user_update.nickname
    
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
    
    return user


@router.get("/session/{session_id}", response_model=UserResponse)
def get_user_by_session(session_id: str, db: Session = Depends(get_db)):
    """Get user by session ID."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/nickname/{nickname}", response_model=UserResponse)
def get_user_by_nickname(nickname: str, db: Session = Depends(get_db)):
    """Get user by nickname."""
    user = db.query(User).filter(User.nickname == nickname).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

