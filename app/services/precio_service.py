from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.precio import Precio
from ..schemas.precio import PrecioCreate, PrecioUpdate

class PrecioService:
    @staticmethod
    def create_precio(db: Session, precio: PrecioCreate) -> Precio:
        db_precio = Precio(**precio.dict())
        db.add(db_precio)
        db.commit()
        db.refresh(db_precio)
        return db_precio
    
    @staticmethod
    def get_precio(db: Session, precio_id: int) -> Precio:
        db_precio = db.query(Precio).filter(Precio.id == precio_id).first()
        if db_precio is None:
            raise HTTPException(status_code=404, detail="Precio not found")
        return db_precio
    
    @staticmethod
    def get_precios_by_servicio(db: Session, servicio_id: int):
        return db.query(Precio).filter(Precio.servicio_id == servicio_id).all()
    
    @staticmethod
    def update_precio(db: Session, precio_id: int, precio: PrecioUpdate) -> Precio:
        db_precio = PrecioService.get_precio(db, precio_id)
        
        update_data = precio.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_precio, field, value)
        
        db.commit()
        db.refresh(db_precio)
        return db_precio
    
    @staticmethod
    def delete_precio(db: Session, precio_id: int) -> bool:
        db_precio = PrecioService.get_precio(db, precio_id)
        db.delete(db_precio)
        db.commit()
        return True
