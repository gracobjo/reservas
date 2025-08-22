from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.servicio import Servicio
from ..schemas.servicio import ServicioCreate, ServicioUpdate

class ServicioService:
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Servicio]:
        """Obtener todos los servicios con paginación"""
        return db.query(Servicio).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, servicio_id: int) -> Optional[Servicio]:
        """Obtener un servicio por ID"""
        return db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    @staticmethod
    def get_by_nombre(db: Session, nombre: str) -> Optional[Servicio]:
        """Obtener un servicio por nombre"""
        return db.query(Servicio).filter(Servicio.nombre == nombre).first()
    
    @staticmethod
    def create(db: Session, servicio: ServicioCreate) -> Servicio:
        """Crear un nuevo servicio"""
        db_servicio = Servicio(**servicio.dict())
        db.add(db_servicio)
        db.commit()
        db.refresh(db_servicio)
        return db_servicio
    
    @staticmethod
    def update(db: Session, servicio_id: int, servicio: ServicioUpdate) -> Optional[Servicio]:
        """Actualizar un servicio existente"""
        db_servicio = ServicioService.get_by_id(db, servicio_id)
        if not db_servicio:
            return None
        
        # Solo actualizar campos que no sean None
        update_data = servicio.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_servicio, field, value)
        
        db.commit()
        db.refresh(db_servicio)
        return db_servicio
    
    @staticmethod
    def delete(db: Session, servicio_id: int) -> bool:
        """Eliminar un servicio"""
        db_servicio = ServicioService.get_by_id(db, servicio_id)
        if not db_servicio:
            return False
        
        db.delete(db_servicio)
        db.commit()
        return True
    
    @staticmethod
    def search_by_nombre(db: Session, nombre: str) -> List[Servicio]:
        """Buscar servicios por nombre (búsqueda parcial)"""
        return db.query(Servicio).filter(Servicio.nombre.ilike(f"%{nombre}%")).all()
