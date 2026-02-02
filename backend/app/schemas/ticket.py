from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.ticket import TicketStatus, TicketPriority

# Message Schemas
class TicketMessageBase(BaseModel):
    message: str

class TicketMessageCreate(TicketMessageBase):
    pass

class TicketMessageResponse(TicketMessageBase):
    id: int
    ticket_id: int
    user_id: int
    created_at: datetime
    # Optionally include user name if needed, but for now ID is likely enough or we can expand
    user_name: Optional[str] = None

    class Config:
        orm_mode = True

# Ticket Schemas
class TicketBase(BaseModel):
    subject: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None

class TicketResponse(TicketBase):
    id: int
    user_id: int
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessageResponse] = []

    class Config:
        orm_mode = True
