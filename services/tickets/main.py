from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import db_manager
from shared.models import TicketResponse, PurchaseRequest
from shared.auth import get_current_user, require_admin
from datetime import datetime, timedelta
import logging
from typing import List, Optional
import uuid

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineMagic Tickets Service", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_ticket_code() -> str:
    """Generar código único para boleto"""
    return f"CINE-{uuid.uuid4().hex[:8].upper()}"

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    try:
        db_manager.execute_query("SELECT 1")
        return {"status": "healthy", "service": "tickets"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/purchase", response_model=dict)
async def purchase_tickets_and_products(
    purchase: PurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """Comprar boletos y productos"""
    try:
        # Verificar que el usuario coincide
        if purchase.id_usuario != current_user['id_usuario']:
            raise HTTPException(status_code=403, detail="No puedes comprar para otro usuario")
        
        total_calculado = 0
        boletos_creados = []
        productos_comprados = []
        
        # Procesar cada item
        for item in purchase.items:
            if item['type'] == 'ticket':
                # Procesar boleto
                id_funcion = item['id_funcion']
                asiento = item['asiento']
                
                # Verificar que la función existe y está disponible
                funcion = db_manager.execute_query(
                    """SELECT f.*, p.titulo, s.nombre as sala_nombre
                       FROM funciones f
                       JOIN peliculas p ON f.id_pelicula = p.id_pelicula
                       JOIN salas s ON f.id_sala = s.id_sala
                       WHERE f.id_funcion = %s AND f.horario > NOW()""",
                    (id_funcion,)
                )
                
                if not funcion:
                    raise HTTPException(status_code=404, detail=f"Función {id_funcion} no encontrada o ya pasó")
                
                funcion_data = funcion[0]
                
                # Verificar que el asiento está disponible
                asiento_disponible = db_manager.execute_query(
                    """SELECT id_asiento FROM asientos 
                       WHERE id_funcion = %s AND numero_asiento = %s AND estado = 'disponible'""",
                    (id_funcion, asiento)
                )
                
                if not asiento_disponible:
                    raise HTTPException(status_code=400, detail=f"Asiento {asiento} no disponible")
                
                # Reservar asiento
                db_manager.execute_query(
                    "UPDATE asientos SET estado = 'ocupado' WHERE id_asiento = %s",
                    (asiento_disponible[0]['id_asiento'],),
                    fetch=False
                )
                
                # Crear boleto
                codigo_boleto = generate_ticket_code()
                boleto_id = db_manager.execute_query(
                    """INSERT INTO boletos (id_usuario, id_funcion, numero_asiento, precio, codigo_boleto)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (purchase.id_usuario, id_funcion, asiento, funcion_data['precio'], codigo_boleto),
                    fetch=False
                )
                
                boletos_creados.append({
                    'id_boleto': boleto_id,
                    'codigo': codigo_boleto,
                    'pelicula': funcion_data['titulo'],
                    'sala': funcion_data['sala_nombre'],
                    'horario': funcion_data['horario'],
                    'asiento': asiento,
                    'precio': float(funcion_data['precio'])
                })
                
                total_calculado += float(funcion_data['precio'])
                
            elif item['type'] == 'product':
                # Procesar producto
                id_producto = item['id_producto']
                cantidad = item['cantidad']
                
                # Verificar que el producto existe y hay stock
                producto = db_manager.execute_query(
                    "SELECT * FROM productos WHERE id_producto = %s",
                    (id_producto,)
                )
                
                if not producto:
                    raise HTTPException(status_code=404, detail=f"Producto {id_producto} no encontrado")
                
                producto_data = producto[0]
                
                if producto_data['stock'] < cantidad:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente para {producto_data['nombre']}")
                
                # Actualizar stock
                db_manager.execute_query(
                    "UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
                    (cantidad, id_producto),
                    fetch=False
                )
                
                # Registrar venta
                total_producto = float(producto_data['precio']) * cantidad
                venta_id = db_manager.execute_query(
                    """INSERT INTO ventas_productos (id_usuario, id_producto, cantidad, precio_unitario, total)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (purchase.id_usuario, id_producto, cantidad, producto_data['precio'], total_producto),
                    fetch=False
                )
                
                productos_comprados.append({
                    'id_venta': venta_id,
                    'producto': producto_data['nombre'],
                    'cantidad': cantidad,
                    'precio_unitario': float(producto_data['precio']),
                    'total': total_producto
                })
                
                total_calculado += total_producto
        
        # Verificar que el total coincide
        if abs(total_calculado - purchase.total) > 0.01:
            raise HTTPException(status_code=400, detail="El total no coincide con los items seleccionados")
        
        logger.info(f"Compra realizada por usuario {purchase.id_usuario}: ${total_calculado}")
        
        return {
            "message": "Compra realizada exitosamente",
            "total": total_calculado,
            "boletos": boletos_creados,
            "productos": productos_comprados
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/user/{user_id}", response_model=List[TicketResponse])
async def get_user_tickets(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    estado: Optional[str] = None
):
    """Obtener boletos de un usuario"""
    try:
        # Verificar permisos
        if current_user['id_usuario'] != user_id and current_user['rol'] != 'admin':
            raise HTTPException(status_code=403, detail="No tienes permisos para ver estos boletos")
        
        base_query = """
        SELECT b.id_boleto, b.id_usuario, b.id_funcion, b.numero_asiento, b.precio,
               b.fecha_compra, b.estado, b.codigo_boleto,
               p.titulo as pelicula_titulo, s.nombre as sala_nombre, f.horario
        FROM boletos b
        JOIN funciones f ON b.id_funcion = f.id_funcion
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        WHERE b.id_usuario = %s
        """
        
        params = [user_id]
        
        if estado:
            base_query += " AND b.estado = %s"
            params.append(estado)
        
        base_query += " ORDER BY f.horario DESC"
        
        tickets = db_manager.execute_query(base_query, tuple(params))
        return tickets
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo boletos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, current_user: dict = Depends(get_current_user)):
    """Obtener boleto por ID"""
    try:
        ticket = db_manager.execute_query(
            """SELECT b.id_boleto, b.id_usuario, b.id_funcion, b.numero_asiento, b.precio,
                      b.fecha_compra, b.estado, b.codigo_boleto,
                      p.titulo as pelicula_titulo, s.nombre as sala_nombre, f.horario
               FROM boletos b
               JOIN funciones f ON b.id_funcion = f.id_funcion
               JOIN peliculas p ON f.id_pelicula = p.id_pelicula
               JOIN salas s ON f.id_sala = s.id_sala
               WHERE b.id_boleto = %s""",
            (ticket_id,)
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Boleto no encontrado")
        
        ticket_data = ticket[0]
        
        # Verificar permisos
        if current_user['id_usuario'] != ticket_data['id_usuario'] and current_user['rol'] != 'admin':
            raise HTTPException(status_code=403, detail="No tienes permisos para ver este boleto")
        
        return ticket_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo boleto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/{ticket_id}/cancel")
async def cancel_ticket(ticket_id: int, current_user: dict = Depends(get_current_user)):
    """Cancelar boleto"""
    try:
        # Obtener información del boleto
        ticket = db_manager.execute_query(
            """SELECT b.*, f.horario
               FROM boletos b
               JOIN funciones f ON b.id_funcion = f.id_funcion
               WHERE b.id_boleto = %s""",
            (ticket_id,)
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Boleto no encontrado")
        
        ticket_data = ticket[0]
        
        # Verificar permisos
        if current_user['id_usuario'] != ticket_data['id_usuario'] and current_user['rol'] != 'admin':
            raise HTTPException(status_code=403, detail="No tienes permisos para cancelar este boleto")
        
        # Verificar que el boleto esté activo
        if ticket_data['estado'] != 'activo':
            raise HTTPException(status_code=400, detail="El boleto ya está cancelado o usado")
        
        # Verificar que la función no haya pasado
        if ticket_data['horario'] <= datetime.now():
            raise HTTPException(status_code=400, detail="No se puede cancelar un boleto de función pasada")
        
        # Verificar tiempo límite para cancelación (2 horas antes)
        tiempo_limite = ticket_data['horario'] - timedelta(hours=2)
        if datetime.now() > tiempo_limite:
            raise HTTPException(status_code=400, detail="No se puede cancelar con menos de 2 horas de anticipación")
        
        # Cancelar boleto
        db_manager.execute_query(
            "UPDATE boletos SET estado = 'cancelado' WHERE id_boleto = %s",
            (ticket_id,),
            fetch=False
        )
        
        # Liberar asiento
        db_manager.execute_query(
            """UPDATE asientos SET estado = 'disponible' 
               WHERE id_funcion = %s AND numero_asiento = %s""",
            (ticket_data['id_funcion'], ticket_data['numero_asiento']),
            fetch=False
        )
        
        # Crear solicitud de devolución
        db_manager.execute_query(
            """INSERT INTO devoluciones (id_boleto, motivo, estado)
               VALUES (%s, 'Cancelación por usuario', 'aprobada')""",
            (ticket_id,),
            fetch=False
        )
        
        logger.info(f"Boleto cancelado: {ticket_id}")
        return {"message": "Boleto cancelado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelando boleto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/{ticket_id}/use")
async def use_ticket(ticket_id: int, current_user: dict = Depends(require_admin)):
    """Marcar boleto como usado (solo admin)"""
    try:
        # Verificar que el boleto existe y está activo
        ticket = db_manager.execute_query(
            "SELECT estado FROM boletos WHERE id_boleto = %s",
            (ticket_id,)
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Boleto no encontrado")
        
        if ticket[0]['estado'] != 'activo':
            raise HTTPException(status_code=400, detail="El boleto no está activo")
        
        # Marcar como usado
        db_manager.execute_query(
            "UPDATE boletos SET estado = 'usado' WHERE id_boleto = %s",
            (ticket_id,),
            fetch=False
        )
        
        logger.info(f"Boleto marcado como usado: {ticket_id}")
        return {"message": "Boleto marcado como usado"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marcando boleto como usado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/sales/stats")
async def get_sales_stats(current_user: dict = Depends(require_admin)):
    """Obtener estadísticas de ventas (solo admin)"""
    try:
        # Estadísticas de boletos
        ticket_stats = db_manager.execute_query(
            """SELECT 
                   COUNT(*) as total_boletos,
                   SUM(precio) as ingresos_boletos,
                   COUNT(CASE WHEN estado = 'activo' THEN 1 END) as boletos_activos,
                   COUNT(CASE WHEN estado = 'usado' THEN 1 END) as boletos_usados,
                   COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as boletos_cancelados
               FROM boletos
               WHERE fecha_compra >= DATE_SUB(NOW(), INTERVAL 30 DAY)"""
        )
        
        # Películas más populares
        popular_movies = db_manager.execute_query(
            """SELECT p.titulo, COUNT(b.id_boleto) as boletos_vendidos, SUM(b.precio) as ingresos
               FROM boletos b
               JOIN funciones f ON b.id_funcion = f.id_funcion
               JOIN peliculas p ON f.id_pelicula = p.id_pelicula
               WHERE b.fecha_compra >= DATE_SUB(NOW(), INTERVAL 30 DAY)
               GROUP BY p.id_pelicula
               ORDER BY boletos_vendidos DESC
               LIMIT 10"""
        )
        
        # Ventas por día
        daily_sales = db_manager.execute_query(
            """SELECT DATE(fecha_compra) as fecha, 
                      COUNT(*) as boletos_vendidos,
                      SUM(precio) as ingresos
               FROM boletos
               WHERE fecha_compra >= DATE_SUB(NOW(), INTERVAL 7 DAY)
               GROUP BY DATE(fecha_compra)
               ORDER BY fecha DESC"""
        )
        
        return {
            "resumen_boletos": ticket_stats[0] if ticket_stats else {},
            "peliculas_populares": popular_movies,
            "ventas_diarias": daily_sales
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/refunds/pending")
async def get_pending_refunds(current_user: dict = Depends(require_admin)):
    """Obtener devoluciones pendientes (solo admin)"""
    try:
        refunds = db_manager.execute_query(
            """SELECT d.id_devolucion, d.motivo, d.fecha_solicitud, d.estado,
                      b.id_boleto, b.precio, b.codigo_boleto,
                      u.nombre as usuario_nombre, u.correo as usuario_correo,
                      p.titulo as pelicula_titulo, f.horario
               FROM devoluciones d
               JOIN boletos b ON d.id_boleto = b.id_boleto
               JOIN usuarios u ON b.id_usuario = u.id_usuario
               JOIN funciones f ON b.id_funcion = f.id_funcion
               JOIN peliculas p ON f.id_pelicula = p.id_pelicula
               WHERE d.estado = 'pendiente'
               ORDER BY d.fecha_solicitud DESC"""
        )
        
        return refunds
        
    except Exception as e:
        logger.error(f"Error obteniendo devoluciones: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/refunds/{refund_id}/approve")
async def approve_refund(refund_id: int, current_user: dict = Depends(require_admin)):
    """Aprobar devolución (solo admin)"""
    try:
        affected_rows = db_manager.execute_query(
            "UPDATE devoluciones SET estado = 'aprobada' WHERE id_devolucion = %s AND estado = 'pendiente'",
            (refund_id,),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Devolución no encontrada o ya procesada")
        
        logger.info(f"Devolución aprobada: {refund_id}")
        return {"message": "Devolución aprobada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aprobando devolución: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
