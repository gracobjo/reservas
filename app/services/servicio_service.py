from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.servicio import Servicio
from ..schemas.servicio import ServicioCreate, ServicioUpdate

class ServicioService:
    @staticmethod
    def create_servicio(db: Session, servicio: ServicioCreate) -> Servicio:
        db_servicio = Servicio(**servicio.dict())
        db.add(db_servicio)
        db.commit()
        db.refresh(db_servicio)
        return db_servicio
    
    @staticmethod
    def get_servicio(db: Session, servicio_id: int) -> Servicio:
        db_servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if db_servicio is None:
            raise HTTPException(status_code=404, detail="Servicio not found")
        return db_servicio
    
    @staticmethod
    def get_servicios(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Servicio).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_servicio(db: Session, servicio_id: int, servicio: ServicioUpdate) -> Servicio:
        db_servicio = ServicioService.get_servicio(db, servicio_id)
        
        update_data = servicio.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_servicio, field, value)
        
        db.commit()
        db.refresh(db_servicio)
        return db_servicio
    
    @staticmethod
    def delete_servicio(db: Session, servicio_id: int) -> bool:
        db_servicio = ServicioService.get_servicio(db, servicio_id)
        db.delete(db_servicio)
        db.commit()
        return True
