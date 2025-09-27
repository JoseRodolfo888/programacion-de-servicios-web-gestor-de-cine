from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    nombre: str
    edad: int
    correo: EmailStr
    
    @validator('edad')
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError('La edad debe estar entre 0 y 120 años')
        return v

class UserCreate(UserBase):
    contrasena: str
    
    @validator('contrasena')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

class UserResponse(UserBase):
    id_usuario: int
    id_rol: int
    rol: str
    fecha_registro: datetime

class UserLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class MovieBase(BaseModel):
    titulo: str
    director: str
    duracion: int
    clasificacion: str
    genero: str
    sinopsis: Optional[str] = None
    
    @validator('duracion')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('La duración debe ser mayor a 0')
        return v

class MovieCreate(MovieBase):
    imagen_url: Optional[str] = None
    trailer_url: Optional[str] = None

class MovieResponse(MovieBase):
    id_pelicula: int
    imagen_url: Optional[str] = None
    trailer_url: Optional[str] = None
    fecha_creacion: datetime

class TheaterBase(BaseModel):
    nombre: str
    capacidad: int
    tipo: str
    
    @validator('capacidad')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('La capacidad debe ser mayor a 0')
        return v

class TheaterResponse(TheaterBase):
    id_sala: int

class ShowtimeBase(BaseModel):
    id_pelicula: int
    id_sala: int
    horario: datetime
    precio: float
    
    @validator('precio')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v

class ShowtimeResponse(ShowtimeBase):
    id_funcion: int
    pelicula_titulo: str
    sala_nombre: str
    asientos_disponibles: int

class ProductBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria: str
    stock: int
    
    @validator('precio')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v
    
    @validator('stock')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v

class ProductCreate(ProductBase):
    imagen_url: Optional[str] = None

class ProductResponse(ProductBase):
    id_producto: int
    imagen_url: Optional[str] = None
    fecha_creacion: datetime

class TicketBase(BaseModel):
    id_usuario: int
    id_funcion: int
    numero_asiento: int
    precio: float

class TicketResponse(TicketBase):
    id_boleto: int
    pelicula_titulo: str
    sala_nombre: str
    horario: datetime
    fecha_compra: datetime
    estado: str
    codigo_boleto: Optional[str] = None

class PurchaseRequest(BaseModel):
    id_usuario: int
    items: List[dict]  # [{"type": "ticket", "id_funcion": 1, "asiento": 5}, {"type": "product", "id_producto": 1, "cantidad": 2}]
    total: float
