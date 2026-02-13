from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.rbac import get_current_user as get_current_active_user
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate, TicketMessageCreate, TicketMessageResponse
from app.models.user import User
from app.services.ticket_service import ticket_service

router = APIRouter()

@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return ticket_service.create_ticket(db=db, ticket=ticket, user_id=current_user.id)

@router.get("/", response_model=List[TicketResponse])
def read_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return ticket_service.get_tickets(
        db=db,
        user_id=current_user.id,
        is_admin=current_user.is_superuser,
        skip=skip,
        limit=limit
    )

@router.get("/{ticket_id}", response_model=TicketResponse)
def read_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ticket = ticket_service.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        is_admin=current_user.is_superuser
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ticket = ticket_service.update_ticket(
        db=db,
        ticket_id=ticket_id,
        ticket_update=ticket_update,
        user_id=current_user.id,
        is_admin=current_user.is_superuser
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/messages", response_model=TicketMessageResponse)
def create_ticket_message(
    ticket_id: int,
    message: TicketMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ticket = ticket_service.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        is_admin=current_user.is_superuser
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket_service.add_message(
        db=db,
        ticket_id=ticket_id,
        message=message,
        user_id=current_user.id
    )
