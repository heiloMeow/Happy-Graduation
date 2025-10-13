"""Message management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Message, Table, TableMember, ReplyType
from app.schemas import MessageSend, MessageReply, MessageResponse
from app.routers.ws import manager

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/send", response_model=MessageResponse)
async def send_message(msg: MessageSend, db: Session = Depends(get_db)):
    """Send a message to specific user or whole table."""
    from_table = db.query(Table).filter(Table.id == msg.from_table_id).first()
    to_table = db.query(Table).filter(Table.id == msg.to_table_id).first()
    
    if not from_table or not to_table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    db_message = Message(
        from_table_id=msg.from_table_id,
        to_table_id=msg.to_table_id,
        content=msg.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Determine recipient(s)
    if msg.to_user_id:
        # Send to specific user only
        member_ids = [msg.to_user_id]
    else:
        # Send to whole table
        to_members = db.query(TableMember).filter(TableMember.table_id == msg.to_table_id).all()
        member_ids = [m.user_id for m in to_members]
    
    await manager.broadcast_to_table(
        msg.to_table_id,
        member_ids,
        {
            "type": "message_received",
            "data": {
                "id": db_message.id,
                "from_table_number": from_table.number,
                "content": db_message.content
            }
        }
    )
    
    return db_message


@router.put("/{message_id}/reply", response_model=MessageResponse)
async def reply_message(message_id: int, reply: MessageReply, db: Session = Depends(get_db)):
    """Reply to a message."""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    try:
        message.reply = ReplyType(reply.reply)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reply type")
    
    db.commit()
    db.refresh(message)
    
    from_members = db.query(TableMember).filter(TableMember.table_id == message.from_table_id).all()
    member_ids = [m.user_id for m in from_members]
    
    # Exclude replier from receiving their own reply
    if reply.replier_user_id:
        member_ids = [uid for uid in member_ids if uid != reply.replier_user_id]
    
    to_table = db.query(Table).filter(Table.id == message.to_table_id).first()
    
    await manager.broadcast_to_table(
        message.from_table_id,
        member_ids,
        {
            "type": "message_reply",
            "data": {
                "id": message.id,
                "from_table_number": to_table.number,
                "reply": message.reply.value,
                "original_content": message.content
            }
        }
    )
    
    return message


@router.get("/table/{table_id}", response_model=list[MessageResponse])
def get_table_messages(table_id: int, db: Session = Depends(get_db)):
    """Get all messages for a table (sent and received)."""
    sent = db.query(Message).filter(Message.from_table_id == table_id).all()
    received = db.query(Message).filter(Message.to_table_id == table_id).all()
    
    all_messages = sent + received
    all_messages.sort(key=lambda x: x.timestamp)
    
    return all_messages

