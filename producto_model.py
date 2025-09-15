class ProductoModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_todos_productos(self):
        """Obtiene todos los productos"""
        query = "SELECT * FROM productos ORDER BY nombre"
        return self.db.ejecutar_consulta(query).fetchall()
    
    def obtener_producto_por_id(self, id_producto):
        """Obtiene un producto por su ID"""
        query = "SELECT * FROM productos WHERE id_producto = %s"
        return self.db.ejecutar_consulta(query, (id_producto,)).fetchone()
    
    def obtener_productos_con_stock(self):
        """Obtiene productos con stock disponible"""
        query = "SELECT * FROM productos WHERE stock > 0 ORDER BY nombre"
        return self.db.ejecutar_consulta(query).fetchall()
    
    def agregar_producto(self, nombre, precio, stock):
        """Agrega un nuevo producto"""
        query = "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)"
        self.db.ejecutar_consulta(query, (nombre, precio, stock))
        self.db.commit()
    
    def actualizar_producto(self, id_producto, nombre, precio):
        """Actualiza un producto existente"""
        query = "UPDATE productos SET nombre = %s, precio = %s WHERE id_producto = %s"
        self.db.ejecutar_consulta(query, (nombre, precio, id_producto))
        self.db.commit()
    
    def eliminar_producto(self, id_producto):
        """Elimina un producto y sus movimientos relacionados"""
        try:
            # Primero eliminar movimientos relacionados
            query_movimientos = "DELETE FROM movimientos_inventario WHERE id_producto = %s"
            self.db.ejecutar_consulta(query_movimientos, (id_producto,))
            
            # Luego eliminar el producto
            query_producto = "DELETE FROM productos WHERE id_producto = %s"
            self.db.ejecutar_consulta(query_producto, (id_producto,))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar producto: {e}")
    
    def actualizar_stock(self, id_producto, cantidad):
        """Actualiza el stock de un producto"""
        query = "UPDATE productos SET stock = stock + %s WHERE id_producto = %s"
        self.db.ejecutar_consulta(query, (cantidad, id_producto))
        self.db.commit()
    
    def buscar_producto(self, termino):
        """Busca productos por nombre"""
        query = "SELECT * FROM productos WHERE nombre LIKE %s ORDER BY nombre"
        return self.db.ejecutar_consulta(query, (f"%{termino}%",)).fetchall()