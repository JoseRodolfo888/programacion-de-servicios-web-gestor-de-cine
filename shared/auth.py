from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cinemagic-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def require_admin(token_data: dict = Depends(verify_token)):
    """Verificar que el usuario sea administrador"""
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: se requieren permisos de administrador")
    return token_data

def get_current_user(token_data: dict = Depends(verify_token)):
    """Obtener usuario actual del token"""
    return {
        "id_usuario": token_data.get("sub"),
        "correo": token_data.get("email"),
        "rol": token_data.get("role"),
        "nombre": token_data.get("name")
    }
