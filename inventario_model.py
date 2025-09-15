from datetime import datetime

class InventarioModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def registrar_movimiento(self, id_producto, cantidad, tipo, motivo=""):
        """Registra un movimiento de inventario"""
        query = """
        INSERT INTO movimientos_inventario (id_producto, cantidad, tipo, motivo)
        VALUES (%s, %s, %s, %s)
        """
        self.db.ejecutar_consulta(query, (id_producto, cantidad, tipo, motivo))
        self.db.commit()
    
    def obtener_movimientos(self, fecha_inicio=None, fecha_fin=None, id_producto=None):
        """Obtiene movimientos de inventario con filtros opcionales"""
        query = """
        SELECT m.*, p.nombre as producto
        FROM movimientos_inventario m
        JOIN productos p ON m.id_producto = p.id_producto
        WHERE 1=1
        """
        params = []
        
        if fecha_inicio:
            query += " AND m.fecha >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND m.fecha <= %s"
            params.append(fecha_fin)
        
        if id_producto:
            query += " AND m.id_producto = %s"
            params.append(id_producto)
        
        query += " ORDER BY m.fecha DESC"
        
        return self.db.ejecutar_consulta(query, params).fetchall()
    
    def obtener_historial_producto(self, id_producto, limite=50):
        """Obtiene el historial de movimientos de un producto"""
        query = """
        SELECT m.*, p.nombre as producto
        FROM movimientos_inventario m
        JOIN productos p ON m.id_producto = p.id_producto
        WHERE m.id_producto = %s
        ORDER BY m.fecha DESC
        LIMIT %s
        """
        return self.db.ejecutar_consulta(query, (id_producto, limite)).fetchall()
    
    def obtener_estadisticas_movimientos(self, fecha_inicio, fecha_fin):
        """Obtiene estadísticas de movimientos de inventario"""
        query = """
        SELECT 
            p.nombre as producto,
            SUM(CASE WHEN m.tipo = 'entrada' THEN m.cantidad ELSE 0 END) as entradas,
            SUM(CASE WHEN m.tipo = 'salida' THEN m.cantidad ELSE 0 END) as salidas,
            p.stock as stock_actual
        FROM movimientos_inventario m
        JOIN productos p ON m.id_producto = p.id_producto
        WHERE m.fecha BETWEEN %s AND %s
        GROUP BY m.id_producto
        ORDER BY salidas DESC
        """
        return self.db.ejecutar_consulta(query, (fecha_inicio, fecha_fin)).fetchall()