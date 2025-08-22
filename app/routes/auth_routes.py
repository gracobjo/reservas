from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import timedelta
from ..db_sqlite_clean import get_db
from ..services.auth_service import AuthService, get_current_user, require_admin
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/auth", tags=["autenticacion"])

@router.post("/login", response_model=Dict[str, Any])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Iniciar sesión y obtener token de acceso"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "rol": user.rol},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds(),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
            "activo": user.activo
        }
    }

@router.post("/register", response_model=Dict[str, Any])
def register(
    username: str,
    password: str,
    email: str,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    try:
        user = AuthService.create_user(db, username, password, email)
        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol,
                "activo": user.activo
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/me", response_model=Dict[str, Any])
def get_current_user_info(current_user = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "rol": current_user.rol,
        "activo": current_user.activo,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.post("/refresh", response_model=Dict[str, Any])
def refresh_token(current_user = Depends(get_current_user)):
    """Refrescar token de acceso"""
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": current_user.username, "rol": current_user.rol},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds()
    }

@router.post("/change-password", response_model=BaseResponse)
def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cambiar contraseña del usuario actual"""
    # Verificar contraseña actual
    if not AuthService.verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Generar nuevo hash
    new_password_hash = AuthService.hash_password(new_password)
    current_user.password_hash = new_password_hash
    
    db.commit()
    
    return BaseResponse(
        success=True,
        message="Contraseña cambiada exitosamente"
    )

@router.post("/admin/create-user", response_model=Dict[str, Any])
def create_user_admin(
    username: str,
    password: str,
    email: str,
    rol: str = "usuario",
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Crear usuario (solo admin)"""
    try:
        user = AuthService.create_user(db, username, password, email, rol)
        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol,
                "activo": user.activo
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/admin/users/{user_id}/toggle-status", response_model=BaseResponse)
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Activar/desactivar usuario (solo admin)"""
    from ..models.usuario import Usuario
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # No permitir desactivar al admin actual
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")
    
    user.activo = not user.activo
    db.commit()
    
    status = "activado" if user.activo else "desactivado"
    return BaseResponse(
        success=True,
        message=f"Usuario {status} exitosamente"
    )

@router.put("/admin/users/{user_id}/change-role", response_model=BaseResponse)
def change_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Cambiar rol de usuario (solo admin)"""
    from ..models.usuario import Usuario
    
    if new_role not in ["usuario", "analista", "admin"]:
        raise HTTPException(status_code=400, detail="Rol inválido")
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # No permitir cambiar rol del admin actual
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol")
    
    old_role = user.rol
    user.rol = new_role
    db.commit()
    
    return BaseResponse(
        success=True,
        message=f"Rol cambiado de '{old_role}' a '{new_role}' exitosamente"
    )

@router.get("/admin/users", response_model=Dict[str, Any])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Listar usuarios (solo admin)"""
    from ..models.usuario import Usuario
    
    users = db.query(Usuario).offset(skip).limit(limit).all()
    
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
            "activo": user.activo,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return {
        "users": user_list,
        "total": len(user_list),
        "skip": skip,
        "limit": limit
    }
