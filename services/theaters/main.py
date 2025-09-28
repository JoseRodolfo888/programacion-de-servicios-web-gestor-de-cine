from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import db_manager
from shared.models import TheaterBase, TheaterResponse, ShowtimeBase, ShowtimeResponse
from shared.auth import require_admin, get_current_user
from datetime import datetime, timedelta
import logging
from typing import List, Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineMagic Theaters Service", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_seats_for_showtime(showtime_id: int, theater_capacity: int):
    """Crear asientos para una función"""
    try:
        # Crear asientos numerados del 1 al capacity
        seats_data = [(showtime_id, seat_num) for seat_num in range(1, theater_capacity + 1)]
        
        db_manager.execute_many(
            "INSERT INTO asientos (id_funcion, numero_asiento) VALUES (%s, %s)",
            seats_data
        )
        
        logger.info(f"Creados {theater_capacity} asientos para función {showtime_id}")
    except Exception as e:
        logger.error(f"Error creando asientos: {e}")
        raise

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    try:
        db_manager.execute_query("SELECT 1")
        return {"status": "healthy", "service": "theaters"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# GESTIÓN DE SALAS

@app.get("/theaters", response_model=List[TheaterResponse])
async def get_theaters():
    """Obtener todas las salas"""
    try:
        theaters = db_manager.execute_query(
            "SELECT id_sala, nombre, capacidad, tipo FROM salas ORDER BY nombre"
        )
        return theaters
    except Exception as e:
        logger.error(f"Error obteniendo salas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/theaters/{theater_id}", response_model=TheaterResponse)
async def get_theater(theater_id: int):
    """Obtener sala por ID"""
    try:
        theater = db_manager.execute_query(
            "SELECT id_sala, nombre, capacidad, tipo FROM salas WHERE id_sala = %s",
            (theater_id,)
        )
        
        if not theater:
            raise HTTPException(status_code=404, detail="Sala no encontrada")
        
        return theater[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo sala: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/theaters", response_model=dict)
async def create_theater(theater: TheaterBase, current_user: dict = Depends(require_admin)):
    """Crear nueva sala (solo admin)"""
    try:
        theater_id = db_manager.execute_query(
            "INSERT INTO salas (nombre, capacidad, tipo) VALUES (%s, %s, %s)",
            (theater.nombre, theater.capacidad, theater.tipo),
            fetch=False
        )
        
        logger.info(f"Sala creada: {theater.nombre} (ID: {theater_id})")
        return {
            "message": "Sala creada exitosamente",
            "theater_id": theater_id
        }
        
    except Exception as e:
        logger.error(f"Error creando sala: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/theaters/{theater_id}")
async def update_theater(theater_id: int, theater: TheaterBase, current_user: dict = Depends(require_admin)):
    """Actualizar sala (solo admin)"""
    try:
        affected_rows = db_manager.execute_query(
            "UPDATE salas SET nombre = %s, capacidad = %s, tipo = %s WHERE id_sala = %s",
            (theater.nombre, theater.capacidad, theater.tipo, theater_id),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Sala no encontrada")
        
        logger.info(f"Sala actualizada: {theater_id}")
        return {"message": "Sala actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando sala: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/theaters/{theater_id}")
async def delete_theater(theater_id: int, current_user: dict = Depends(require_admin)):
    """Eliminar sala (solo admin)"""
    try:
        # Verificar si hay funciones programadas
        existing_showtimes = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM funciones WHERE id_sala = %s AND horario > NOW()",
            (theater_id,)
        )
        
        if existing_showtimes[0]['count'] > 0:
            raise HTTPException(status_code=400, detail="No se puede eliminar la sala: tiene funciones programadas")
        
        affected_rows = db_manager.execute_query(
            "DELETE FROM salas WHERE id_sala = %s",
            (theater_id,),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Sala no encontrada")
        
        logger.info(f"Sala eliminada: {theater_id}")
        return {"message": "Sala eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando sala: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# GESTIÓN DE FUNCIONES

@app.get("/showtimes", response_model=List[ShowtimeResponse])
async def get_showtimes(
    movie_id: Optional[int] = None,
    theater_id: Optional[int] = None,
    date: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Obtener funciones con filtros opcionales"""
    try:
        base_query = """
        SELECT f.id_funcion, f.id_pelicula, f.id_sala, f.horario, f.precio,
               p.titulo as pelicula_titulo, s.nombre as sala_nombre,
               COUNT(a.id_asiento) as asientos_disponibles
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
        WHERE f.horario > NOW()
        """
        
        params = []
        
        if movie_id:
            base_query += " AND f.id_pelicula = %s"
            params.append(movie_id)
        
        if theater_id:
            base_query += " AND f.id_sala = %s"
            params.append(theater_id)
        
        if date:
            base_query += " AND DATE(f.horario) = %s"
            params.append(date)
        
        base_query += """
        GROUP BY f.id_funcion
        ORDER BY f.horario
        LIMIT %s OFFSET %s
        """
        params.extend([limit, skip])
        
        showtimes = db_manager.execute_query(base_query, tuple(params))
        return showtimes
        
    except Exception as e:
        logger.error(f"Error obteniendo funciones: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/showtimes/{showtime_id}", response_model=ShowtimeResponse)
async def get_showtime(showtime_id: int):
    """Obtener función por ID"""
    try:
        showtime = db_manager.execute_query(
            """SELECT f.id_funcion, f.id_pelicula, f.id_sala, f.horario, f.precio,
                      p.titulo as pelicula_titulo, s.nombre as sala_nombre,
                      COUNT(a.id_asiento) as asientos_disponibles
               FROM funciones f
               JOIN peliculas p ON f.id_pelicula = p.id_pelicula
               JOIN salas s ON f.id_sala = s.id_sala
               LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
               WHERE f.id_funcion = %s
               GROUP BY f.id_funcion""",
            (showtime_id,)
        )
        
        if not showtime:
            raise HTTPException(status_code=404, detail="Función no encontrada")
        
        return showtime[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo función: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/showtimes", response_model=dict)
async def create_showtime(showtime: ShowtimeBase, current_user: dict = Depends(require_admin)):
    """Crear nueva función (solo admin)"""
    try:
        # Verificar que la película existe
        movie = db_manager.execute_query(
            "SELECT id_pelicula FROM peliculas WHERE id_pelicula = %s",
            (showtime.id_pelicula,)
        )
        if not movie:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        # Verificar que la sala existe y obtener capacidad
        theater = db_manager.execute_query(
            "SELECT id_sala, capacidad FROM salas WHERE id_sala = %s",
            (showtime.id_sala,)
        )
        if not theater:
            raise HTTPException(status_code=404, detail="Sala no encontrada")
        
        # Verificar que no haya conflicto de horarios
        conflict = db_manager.execute_query(
            """SELECT id_funcion FROM funciones 
               WHERE id_sala = %s 
               AND ABS(TIMESTAMPDIFF(MINUTE, horario, %s)) < 180""",
            (showtime.id_sala, showtime.horario)
        )
        
        if conflict:
            raise HTTPException(status_code=400, detail="Conflicto de horarios: debe haber al menos 3 horas entre funciones")
        
        # Crear función
        showtime_id = db_manager.execute_query(
            "INSERT INTO funciones (id_pelicula, id_sala, horario, precio) VALUES (%s, %s, %s, %s)",
            (showtime.id_pelicula, showtime.id_sala, showtime.horario, showtime.precio),
            fetch=False
        )
        
        # Crear asientos para la función
        create_seats_for_showtime(showtime_id, theater[0]['capacidad'])
        
        logger.info(f"Función creada: {showtime_id}")
        return {
            "message": "Función creada exitosamente",
            "showtime_id": showtime_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando función: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/showtimes/{showtime_id}")
async def update_showtime(showtime_id: int, showtime: ShowtimeBase, current_user: dict = Depends(require_admin)):
    """Actualizar función (solo admin)"""
    try:
        # Verificar que la función existe
        existing = db_manager.execute_query(
            "SELECT id_funcion FROM funciones WHERE id_funcion = %s",
            (showtime_id,)
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Función no encontrada")
        
        # Verificar que no hay boletos vendidos
        tickets = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM boletos WHERE id_funcion = %s",
            (showtime_id,)
        )
        
        if tickets[0]['count'] > 0:
            raise HTTPException(status_code=400, detail="No se puede modificar: ya hay boletos vendidos")
        
        # Verificar conflicto de horarios (excluyendo la función actual)
        conflict = db_manager.execute_query(
            """SELECT id_funcion FROM funciones 
               WHERE id_sala = %s 
               AND id_funcion != %s
               AND ABS(TIMESTAMPDIFF(MINUTE, horario, %s)) < 180""",
            (showtime.id_sala, showtime_id, showtime.horario)
        )
        
        if conflict:
            raise HTTPException(status_code=400, detail="Conflicto de horarios: debe haber al menos 3 horas entre funciones")
        
        # Actualizar función
        affected_rows = db_manager.execute_query(
            "UPDATE funciones SET id_pelicula = %s, id_sala = %s, horario = %s, precio = %s WHERE id_funcion = %s",
            (showtime.id_pelicula, showtime.id_sala, showtime.horario, showtime.precio, showtime_id),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Función no encontrada")
        
        logger.info(f"Función actualizada: {showtime_id}")
        return {"message": "Función actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando función: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/showtimes/{showtime_id}")
async def delete_showtime(showtime_id: int, current_user: dict = Depends(require_admin)):
    """Eliminar función (solo admin)"""
    try:
        # Verificar que no hay boletos vendidos
        tickets = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM boletos WHERE id_funcion = %s",
            (showtime_id,)
        )
        
        if tickets[0]['count'] > 0:
            raise HTTPException(status_code=400, detail="No se puede eliminar: ya hay boletos vendidos")
        
        affected_rows = db_manager.execute_query(
            "DELETE FROM funciones WHERE id_funcion = %s",
            (showtime_id,),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Función no encontrada")
        
        logger.info(f"Función eliminada: {showtime_id}")
        return {"message": "Función eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando función: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/showtimes/{showtime_id}/seats")
async def get_showtime_seats(showtime_id: int):
    """Obtener asientos de una función"""
    try:
        seats = db_manager.execute_query(
            """SELECT id_asiento, numero_asiento, estado
               FROM asientos 
               WHERE id_funcion = %s 
               ORDER BY numero_asiento""",
            (showtime_id,)
        )
        
        return seats
    except Exception as e:
        logger.error(f"Error obteniendo asientos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/schedule")
async def get_schedule(date: Optional[str] = None):
    """Obtener programación del día"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        schedule = db_manager.execute_query(
            """SELECT f.id_funcion, f.horario, f.precio,
                      p.titulo, p.duracion, p.clasificacion, p.imagen_url,
                      s.nombre as sala, s.tipo as sala_tipo,
                      COUNT(a.id_asiento) as asientos_disponibles
               FROM funciones f
               JOIN peliculas p ON f.id_pelicula = p.id_pelicula
               JOIN salas s ON f.id_sala = s.id_sala
               LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
               WHERE DATE(f.horario) = %s
               GROUP BY f.id_funcion
               ORDER BY f.horario""",
            (date,)
        )
        
        return schedule
    except Exception as e:
        logger.error(f"Error obteniendo programación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
