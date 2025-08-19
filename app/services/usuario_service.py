from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.usuario import Usuario
from ..schemas.usuario import UsuarioCreate, UsuarioUpdate
from ..auth import get_password_hash, verify_password

class UsuarioService:
    @staticmethod
    def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
        # Check if username already exists
        db_usuario = db.query(Usuario).filter(Usuario.username == usuario.username).first()
        if db_usuario:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email already exists
        db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if db_usuario:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = get_password_hash(usuario.password)
        db_usuario = Usuario(
            username=usuario.username,
            email=usuario.email,
            hashed_password=hashed_password
        )
        
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    
    @staticmethod
    def get_usuario(db: Session, usuario_id: int) -> Usuario:
        db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if db_usuario is None:
            raise HTTPException(status_code=404, detail="Usuario not found")
        return db_usuario
    
    @staticmethod
    def get_usuario_by_username(db: Session, username: str) -> Usuario:
        return db.query(Usuario).filter(Usuario.username == username).first()
    
    @staticmethod
    def authenticate_usuario(db: Session, username: str, password: str) -> Usuario:
        usuario = UsuarioService.get_usuario_by_username(db, username)
        if not usuario:
            return None
        if not verify_password(password, usuario.hashed_password):
            return None
        return usuario
    
    @staticmethod
    def update_usuario(db: Session, usuario_id: int, usuario: UsuarioUpdate) -> Usuario:
        db_usuario = UsuarioService.get_usuario(db, usuario_id)
        
        update_data = usuario.dict(exclude_unset=True)
        
        # Hash password if updating
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_usuario, field, value)
        
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    
    @staticmethod
    def delete_usuario(db: Session, usuario_id: int) -> bool:
        db_usuario = UsuarioService.get_usuario(db, usuario_id)
        db.delete(db_usuario)
        db.commit()
        return True
