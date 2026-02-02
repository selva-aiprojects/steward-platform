from sqlalchemy.orm import Session
from app.models.ticket import Ticket, TicketMessage, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketMessageCreate
from typing import List, Optional

class TicketService:
    @staticmethod
    def create_ticket(db: Session, ticket: TicketCreate, user_id: int) -> Ticket:
        db_ticket = Ticket(
            user_id=user_id,
            subject=ticket.subject,
            description=ticket.description,
            priority=ticket.priority
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket

    @staticmethod
    def get_tickets(db: Session, user_id: int, is_admin: bool = False, skip: int = 0, limit: int = 100) -> List[Ticket]:
        if is_admin:
            return db.query(Ticket).offset(skip).limit(limit).all()
        return db.query(Ticket).filter(Ticket.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_ticket(db: Session, ticket_id: int, user_id: int, is_admin: bool = False) -> Optional[Ticket]:
        query = db.query(Ticket).filter(Ticket.id == ticket_id)
        if not is_admin:
            query = query.filter(Ticket.user_id == user_id)
        return query.first()

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_update: TicketUpdate, user_id: int, is_admin: bool = False) -> Optional[Ticket]:
        db_ticket = TicketService.get_ticket(db, ticket_id, user_id, is_admin)
        if not db_ticket:
            return None
        
        update_data = ticket_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ticket, key, value)
            
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket

    @staticmethod
    def add_message(db: Session, ticket_id: int, message: TicketMessageCreate, user_id: int) -> TicketMessage:
        db_message = TicketMessage(
            ticket_id=ticket_id,
            user_id=user_id,
            message=message.message
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

ticket_service = TicketService()
