from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.recurso import Recurso
from ..schemas.recurso import RecursoCreate, RecursoUpdate

class RecursoService:
    @staticmethod
    def create_recurso(db: Session, recurso: RecursoCreate) -> Recurso:
        db_recurso = Recurso(**recurso.dict())
        db.add(db_recurso)
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    
    @staticmethod
    def get_recurso(db: Session, recurso_id: int) -> Recurso:
        db_recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
        if db_recurso is None:
            raise HTTPException(status_code=404, detail="Recurso not found")
        return db_recurso
    
    @staticmethod
    def get_recursos(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Recurso).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_recursos_disponibles(db: Session):
        return db.query(Recurso).filter(Recurso.disponible == True).all()
    
    @staticmethod
    def update_recurso(db: Session, recurso_id: int, recurso: RecursoUpdate) -> Recurso:
        db_recurso = RecursoService.get_recurso(db, recurso_id)
        
        update_data = recurso.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_recurso, field, value)
        
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    
    @staticmethod
    def delete_recurso(db: Session, recurso_id: int) -> bool:
        db_recurso = RecursoService.get_recurso(db, recurso_id)
        db.delete(db_recurso)
        db.commit()
        return True
