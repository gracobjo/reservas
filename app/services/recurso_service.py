from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.recurso import Recurso
from ..schemas.recurso import RecursoCreate, RecursoUpdate

class RecursoService:
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Recurso]:
        """Obtener todos los recursos con paginación"""
        return db.query(Recurso).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, recurso_id: int) -> Optional[Recurso]:
        """Obtener un recurso por ID"""
        return db.query(Recurso).filter(Recurso.id == recurso_id).first()
    
    @staticmethod
    def get_by_nombre(db: Session, nombre: str) -> Optional[Recurso]:
        """Obtener un recurso por nombre"""
        return db.query(Recurso).filter(Recurso.nombre == nombre).first()
    
    @staticmethod
    def get_by_tipo(db: Session, tipo: str) -> List[Recurso]:
        """Obtener recursos por tipo"""
        return db.query(Recurso).filter(Recurso.tipo == tipo).all()
    
    @staticmethod
    def get_disponibles(db: Session) -> List[Recurso]:
        """Obtener solo recursos disponibles"""
        return db.query(Recurso).filter(Recurso.disponible == True).all()
    
    @staticmethod
    def create(db: Session, recurso: RecursoCreate) -> Recurso:
        """Crear un nuevo recurso"""
        db_recurso = Recurso(**recurso.dict())
        db.add(db_recurso)
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    
    @staticmethod
    def update(db: Session, recurso_id: int, recurso: RecursoUpdate) -> Optional[Recurso]:
        """Actualizar un recurso existente"""
        db_recurso = RecursoService.get_by_id(db, recurso_id)
        if not db_recurso:
            return None
        
        # Solo actualizar campos que no sean None
        update_data = recurso.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_recurso, field, value)
        
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    
    @staticmethod
    def delete(db: Session, recurso_id: int) -> bool:
        """Eliminar un recurso"""
        db_recurso = RecursoService.get_by_id(db, recurso_id)
        if not db_recurso:
            return False
        
        db.delete(db_recurso)
        db.commit()
        return True
    
    @staticmethod
    def toggle_disponibilidad(db: Session, recurso_id: int) -> Optional[Recurso]:
        """Cambiar la disponibilidad de un recurso"""
        db_recurso = RecursoService.get_by_id(db, recurso_id)
        if not db_recurso:
            return None
        
        db_recurso.disponible = not db_recurso.disponible
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    
    @staticmethod
    def search_by_nombre(db: Session, nombre: str) -> List[Recurso]:
        """Buscar recursos por nombre (búsqueda parcial)"""
        return db.query(Recurso).filter(Recurso.nombre.ilike(f"%{nombre}%")).all()
