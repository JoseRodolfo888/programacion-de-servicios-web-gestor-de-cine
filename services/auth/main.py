from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import db_manager
from shared.models import UserCreate, UserResponse, UserLogin
from shared.auth import create_access_token, verify_token, get_current_user
import hashlib
from datetime import timedelta
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineMagic Auth Service", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def hash_password(password: str) -> str:
    """Hashear contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return hash_password(password) == hashed_password

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    try:
        # Probar conexión a la base de datos
        db_manager.execute_query("SELECT 1")
        return {"status": "healthy", "service": "auth"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/register", response_model=dict)
async def register_user(user: UserCreate):
    """Registrar nuevo usuario"""
    try:
        # Verificar si el correo ya existe
        existing_user = db_manager.execute_query(
            "SELECT id_usuario FROM usuarios WHERE correo = %s",
            (user.correo,)
        )
        
        if existing_user:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
        
        # Hashear contraseña
        hashed_password = hash_password(user.contrasena)
        
        # Insertar usuario
        user_id = db_manager.execute_query(
            """INSERT INTO usuarios (nombre, edad, correo, contrasena, id_rol) 
               VALUES (%s, %s, %s, %s, 2)""",
            (user.nombre, user.edad, user.correo, hashed_password),
            fetch=False
        )
        
        logger.info(f"Usuario registrado: {user.correo}")
        return {
            "message": "Usuario registrado exitosamente",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error registrando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/login", response_model=dict)
async def login_user(credentials: UserLogin):
    """Iniciar sesión"""
    try:
        # Buscar usuario
        user_data = db_manager.execute_query(
            """SELECT u.id_usuario, u.nombre, u.correo, u.contrasena, u.id_rol, r.nombre as rol
               FROM usuarios u
               JOIN roles r ON u.id_rol = r.id_rol
               WHERE u.correo = %s""",
            (credentials.correo,)
        )
        
        if not user_data or not verify_password(credentials.contrasena, user_data[0]['contrasena']):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
        user = user_data[0]
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={
                "sub": user['id_usuario'],
                "email": user['correo'],
                "name": user['nombre'],
                "role": user['rol']
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Usuario logueado: {user['correo']}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id_usuario": user['id_usuario'],
                "nombre": user['nombre'],
                "correo": user['correo'],
                "rol": user['rol']
            }
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        logger.exception("Error inesperado en login")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    try:
        user_data = db_manager.execute_query(
            """SELECT u.id_usuario, u.nombre, u.correo, u.edad, u.fecha_registro, r.nombre as rol
               FROM usuarios u
               JOIN roles r ON u.id_rol = r.id_rol
               WHERE u.id_usuario = %s""",
            (current_user['id_usuario'],)
        )
        
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return user_data[0]
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/users", response_model=list)
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Obtener todos los usuarios (solo admin)"""
    if current_user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        users = db_manager.execute_query(
            """SELECT u.id_usuario, u.nombre, u.correo, u.edad, u.fecha_registro, r.nombre as rol
               FROM usuarios u
               JOIN roles r ON u.id_rol = r.id_rol
               ORDER BY u.fecha_registro DESC"""
        )
        
        return users
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/users/{user_id}/role")
async def update_user_role(user_id: int, new_role: str, current_user: dict = Depends(get_current_user)):
    """Actualizar rol de usuario (solo admin)"""
    if current_user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    if new_role not in ['admin', 'user']:
        raise HTTPException(status_code=400, detail="Rol inválido")
    
    try:
        # Obtener ID del rol
        role_data = db_manager.execute_query(
            "SELECT id_rol FROM roles WHERE nombre = %s",
            (new_role,)
        )
        
        if not role_data:
            raise HTTPException(status_code=400, detail="Rol no encontrado")
        
        # Actualizar usuario
        affected_rows = db_manager.execute_query(
            "UPDATE usuarios SET id_rol = %s WHERE id_usuario = %s",
            (role_data[0]['id_rol'], user_id),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        logger.info(f"Rol actualizado para usuario {user_id}: {new_role}")
        return {"message": "Rol actualizado exitosamente"}
    except Exception as e:
        logger.error(f"Error actualizando rol: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Eliminar usuario (solo admin)"""
    if current_user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    if user_id == current_user['id_usuario']:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    
    try:
        affected_rows = db_manager.execute_query(
            "DELETE FROM usuarios WHERE id_usuario = %s",
            (user_id,),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        logger.info(f"Usuario eliminado: {user_id}")
        return {"message": "Usuario eliminado exitosamente"}
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/validate-token")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """Validar token JWT"""
    return {"valid": True, "user": current_user}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
