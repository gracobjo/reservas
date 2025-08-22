from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import hashlib
import secrets
from ..db_sqlite_clean import get_db
from ..models.usuario import Usuario

# Configuración de JWT
SECRET_KEY = "tu_clave_secreta_super_segura_cambiala_en_produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Esquema de seguridad
security = HTTPBearer()

class AuthService:
    """Servicio de autenticación y autorización"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Token inválido")
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[Usuario]:
        """Autenticar usuario con credenciales"""
        # Buscar usuario por username
        user = db.query(Usuario).filter(Usuario.username == username).first()
        if not user:
            return None
        
        # Verificar password (hash)
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Generar hash de password"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verificar password contra hash"""
        try:
            salt, hash_value = hashed_password.split('$')
            hash_obj = hashlib.sha256()
            hash_obj.update((password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    @staticmethod
    def create_user(db: Session, username: str, password: str, email: str, rol: str = "usuario") -> Usuario:
        """Crear nuevo usuario"""
        # Verificar que el username no exista
        existing_user = db.query(Usuario).filter(Usuario.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username ya existe")
        
        # Verificar que el email no exista
        existing_email = db.query(Usuario).filter(Usuario.email == email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email ya existe")
        
        # Crear usuario
        hashed_password = AuthService.hash_password(password)
        user = Usuario(
            username=username,
            password_hash=hashed_password,
            email=email,
            rol=rol,
            activo=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Usuario:
        """Obtener usuario actual desde token"""
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = db.query(Usuario).filter(Usuario.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        if not user.activo:
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        return user
    
    @staticmethod
    def require_role(required_role: str):
        """Decorador para requerir rol específico"""
        def role_checker(current_user: Usuario):
            if current_user.rol != required_role and current_user.rol != "admin":
                raise HTTPException(
                    status_code=403, 
                    detail=f"Rol '{required_role}' requerido. Tu rol: {current_user.rol}"
                )
            return current_user
        return role_checker
    
    @staticmethod
    def require_admin(current_user: Usuario):
        """Verificar que el usuario sea admin"""
        if current_user.rol != "admin":
            raise HTTPException(status_code=403, detail="Acceso denegado: se requiere rol de administrador")
        return current_user
    
    @staticmethod
    def require_any_role(allowed_roles: list):
        """Decorador para requerir cualquiera de los roles especificados"""
        def role_checker(current_user: Usuario):
            if current_user.rol not in allowed_roles and current_user.rol != "admin":
                raise HTTPException(
                    status_code=403, 
                    detail=f"Uno de estos roles requerido: {allowed_roles}. Tu rol: {current_user.rol}"
                )
            return current_user
        return role_checker

# Funciones de dependencia predefinidas
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Usuario:
    """Obtener usuario actual desde token"""
    return AuthService.get_current_user(credentials, db)

def require_admin(current_user: Usuario = Depends(get_current_user)):
    """Verificar que el usuario sea admin"""
    return AuthService.require_admin(current_user)

def require_any_role(allowed_roles: list):
    """Decorador para requerir cualquiera de los roles especificados"""
    return AuthService.require_any_role(allowed_roles)
