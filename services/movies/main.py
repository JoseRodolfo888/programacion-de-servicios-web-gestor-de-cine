from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import db_manager
from shared.models import MovieCreate, MovieResponse
from shared.auth import require_admin, get_current_user
import aiofiles
import uuid
from PIL import Image
import logging
from typing import Optional, List

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineMagic Movies Service", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de archivos
UPLOAD_DIR = "uploads/movies"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Crear directorio de uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Validar extensión de archivo"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

def generate_unique_filename(original_filename: str) -> str:
    """Generar nombre único para archivo"""
    extension = os.path.splitext(original_filename)[1].lower()
    unique_name = f"{uuid.uuid4()}{extension}"
    return unique_name

async def save_uploaded_file(file: UploadFile, subfolder: str = "") -> str:
    """Guardar archivo subido"""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")
    
    # Crear subdirectorio si es necesario
    save_dir = os.path.join(UPLOAD_DIR, subfolder) if subfolder else UPLOAD_DIR
    os.makedirs(save_dir, exist_ok=True)
    
    # Generar nombre único
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(save_dir, unique_filename)
    
    # Guardar archivo
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Retornar URL relativa
    return f"/uploads/movies/{subfolder}/{unique_filename}" if subfolder else f"/uploads/movies/{unique_filename}"

def optimize_image(file_path: str, max_width: int = 800, quality: int = 85):
    """Optimizar imagen"""
    try:
        with Image.open(file_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar si es necesario
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Guardar optimizada
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        logger.warning(f"No se pudo optimizar imagen {file_path}: {e}")

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    try:
        db_manager.execute_query("SELECT 1")
        return {"status": "healthy", "service": "movies"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/", response_model=List[MovieResponse])
async def get_movies(skip: int = 0, limit: int = 20):
    """Obtener lista de películas"""
    try:
        movies = db_manager.execute_query(
            """SELECT id_pelicula, titulo, director, duracion, clasificacion, genero, 
                      sinopsis, imagen_url, trailer_url, fecha_creacion
               FROM peliculas 
               ORDER BY fecha_creacion DESC 
               LIMIT %s OFFSET %s""",
            (limit, skip)
        )
        return movies
    except Exception as e:
        logger.error(f"Error obteniendo películas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int):
    """Obtener película por ID"""
    try:
        movie = db_manager.execute_query(
            """SELECT id_pelicula, titulo, director, duracion, clasificacion, genero,
                      sinopsis, imagen_url, trailer_url, fecha_creacion
               FROM peliculas WHERE id_pelicula = %s""",
            (movie_id,)
        )
        
        if not movie:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        return movie[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo película: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/", response_model=dict)
async def create_movie(
    titulo: str = Form(...),
    director: str = Form(...),
    duracion: int = Form(...),
    clasificacion: str = Form(...),
    genero: str = Form(...),
    sinopsis: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    trailer: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_admin)
):
    """Crear nueva película (solo admin)"""
    try:
        imagen_url = None
        trailer_url = None
        
        # Procesar imagen si se proporciona
        if imagen:
            if not validate_file_extension(imagen.filename, ALLOWED_IMAGE_EXTENSIONS):
                raise HTTPException(status_code=400, detail="Formato de imagen no válido")
            
            imagen_url = await save_uploaded_file(imagen, "images")
            # Optimizar imagen
            full_path = os.path.join(UPLOAD_DIR, "images", os.path.basename(imagen_url))
            optimize_image(full_path)
        
        # Procesar trailer si se proporciona
        if trailer:
            if not validate_file_extension(trailer.filename, ALLOWED_VIDEO_EXTENSIONS):
                raise HTTPException(status_code=400, detail="Formato de video no válido")
            
            trailer_url = await save_uploaded_file(trailer, "trailers")
        
        # Insertar película en base de datos
        movie_id = db_manager.execute_query(
            """INSERT INTO peliculas (titulo, director, duracion, clasificacion, genero, 
                                    sinopsis, imagen_url, trailer_url)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (titulo, director, duracion, clasificacion, genero, sinopsis, imagen_url, trailer_url),
            fetch=False
        )
        
        logger.info(f"Película creada: {titulo} (ID: {movie_id})")
        return {
            "message": "Película creada exitosamente",
            "movie_id": movie_id,
            "imagen_url": imagen_url,
            "trailer_url": trailer_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando película: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/{movie_id}", response_model=dict)
async def update_movie(
    movie_id: int,
    titulo: Optional[str] = Form(None),
    director: Optional[str] = Form(None),
    duracion: Optional[int] = Form(None),
    clasificacion: Optional[str] = Form(None),
    genero: Optional[str] = Form(None),
    sinopsis: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    trailer: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_admin)
):
    """Actualizar película (solo admin)"""
    try:
        # Verificar que la película existe
        existing_movie = db_manager.execute_query(
            "SELECT * FROM peliculas WHERE id_pelicula = %s",
            (movie_id,)
        )
        
        if not existing_movie:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        movie = existing_movie[0]
        
        # Preparar datos para actualizar
        update_data = {}
        if titulo is not None:
            update_data['titulo'] = titulo
        if director is not None:
            update_data['director'] = director
        if duracion is not None:
            update_data['duracion'] = duracion
        if clasificacion is not None:
            update_data['clasificacion'] = clasificacion
        if genero is not None:
            update_data['genero'] = genero
        if sinopsis is not None:
            update_data['sinopsis'] = sinopsis
        
        # Procesar nueva imagen
        if imagen:
            if not validate_file_extension(imagen.filename, ALLOWED_IMAGE_EXTENSIONS):
                raise HTTPException(status_code=400, detail="Formato de imagen no válido")
            
            # Eliminar imagen anterior si existe
            if movie['imagen_url']:
                old_image_path = os.path.join(".", movie['imagen_url'].lstrip('/'))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            imagen_url = await save_uploaded_file(imagen, "images")
            full_path = os.path.join(UPLOAD_DIR, "images", os.path.basename(imagen_url))
            optimize_image(full_path)
            update_data['imagen_url'] = imagen_url
        
        # Procesar nuevo trailer
        if trailer:
            if not validate_file_extension(trailer.filename, ALLOWED_VIDEO_EXTENSIONS):
                raise HTTPException(status_code=400, detail="Formato de video no válido")
            
            # Eliminar trailer anterior si existe
            if movie['trailer_url']:
                old_trailer_path = os.path.join(".", movie['trailer_url'].lstrip('/'))
                if os.path.exists(old_trailer_path):
                    os.remove(old_trailer_path)
            
            trailer_url = await save_uploaded_file(trailer, "trailers")
            update_data['trailer_url'] = trailer_url
        
        # Actualizar base de datos si hay cambios
        if update_data:
            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values()) + [movie_id]
            
            db_manager.execute_query(
                f"UPDATE peliculas SET {set_clause} WHERE id_pelicula = %s",
                tuple(values),
                fetch=False
            )
        
        logger.info(f"Película actualizada: {movie_id}")
        return {"message": "Película actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando película: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/{movie_id}")
async def delete_movie(movie_id: int, current_user: dict = Depends(require_admin)):
    """Eliminar película (solo admin)"""
    try:
        # Obtener información de la película
        movie = db_manager.execute_query(
            "SELECT imagen_url, trailer_url FROM peliculas WHERE id_pelicula = %s",
            (movie_id,)
        )
        
        if not movie:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        # Eliminar archivos asociados
        movie_data = movie[0]
        if movie_data['imagen_url']:
            image_path = os.path.join(".", movie_data['imagen_url'].lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        if movie_data['trailer_url']:
            trailer_path = os.path.join(".", movie_data['trailer_url'].lstrip('/'))
            if os.path.exists(trailer_path):
                os.remove(trailer_path)
        
        # Eliminar de base de datos
        affected_rows = db_manager.execute_query(
            "DELETE FROM peliculas WHERE id_pelicula = %s",
            (movie_id,),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        logger.info(f"Película eliminada: {movie_id}")
        return {"message": "Película eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando película: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/search/{query}")
async def search_movies(query: str, skip: int = 0, limit: int = 20):
    """Buscar películas por título, director o género"""
    try:
        search_term = f"%{query}%"
        movies = db_manager.execute_query(
            """SELECT id_pelicula, titulo, director, duracion, clasificacion, genero,
                      sinopsis, imagen_url, trailer_url, fecha_creacion
               FROM peliculas 
               WHERE titulo LIKE %s OR director LIKE %s OR genero LIKE %s
               ORDER BY fecha_creacion DESC
               LIMIT %s OFFSET %s""",
            (search_term, search_term, search_term, limit, skip)
        )
        
        return movies
    except Exception as e:
        logger.error(f"Error buscando películas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/genre/{genre}")
async def get_movies_by_genre(genre: str, skip: int = 0, limit: int = 20):
    """Obtener películas por género"""
    try:
        movies = db_manager.execute_query(
            """SELECT id_pelicula, titulo, director, duracion, clasificacion, genero,
                      sinopsis, imagen_url, trailer_url, fecha_creacion
               FROM peliculas 
               WHERE genero = %s
               ORDER BY fecha_creacion DESC
               LIMIT %s OFFSET %s""",
            (genre, limit, skip)
        )
        
        return movies
    except Exception as e:
        logger.error(f"Error obteniendo películas por género: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/stats/genres")
async def get_genre_stats():
    """Obtener estadísticas de géneros"""
    try:
        stats = db_manager.execute_query(
            """SELECT genero, COUNT(*) as cantidad
               FROM peliculas 
               GROUP BY genero
               ORDER BY cantidad DESC"""
        )
        
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
