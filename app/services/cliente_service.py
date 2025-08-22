from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.cliente import Cliente
from ..schemas.cliente import ClienteCreate, ClienteUpdate

class ClienteService:
    @staticmethod
    def create_cliente(db: Session, cliente: ClienteCreate) -> Cliente:
        # Check if email already exists
        db_cliente = db.query(Cliente).filter(Cliente.email == cliente.email).first()
        if db_cliente:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        db_cliente = Cliente(**cliente.dict())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    
    @staticmethod
    def get_clientes(db: Session) -> list[Cliente]:
        """Obtener lista de todos los clientes"""
        return db.query(Cliente).all()
    
    @staticmethod
    def get_cliente(db: Session, cliente_id: int) -> Cliente:
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if db_cliente is None:
            raise HTTPException(status_code=404, detail="Cliente not found")
        return db_cliente
    
    @staticmethod
    def update_cliente(db: Session, cliente_id: int, cliente: ClienteUpdate) -> Cliente:
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        
        update_data = cliente.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cliente, field, value)
        
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    
    @staticmethod
    def delete_cliente(db: Session, cliente_id: int) -> bool:
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        db.delete(db_cliente)
        db.commit()
        return True
