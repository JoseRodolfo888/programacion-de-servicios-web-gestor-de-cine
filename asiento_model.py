class AsientoModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_asientos_por_funcion(self, id_funcion):
        """Obtiene los asientos de una función"""
        query = "SELECT * FROM asientos WHERE id_funcion = %s ORDER BY numero_asiento"
        return self.db.ejecutar_consulta(query, (id_funcion,)).fetchall()
    
    def obtener_asientos_disponibles(self, id_funcion):
        """Obtiene los asientos disponibles de una función"""
        query = "SELECT * FROM asientos WHERE id_funcion = %s AND estado = 'disponible' ORDER BY numero_asiento"
        return self.db.ejecutar_consulta(query, (id_funcion,)).fetchall()
    
    def generar_asientos(self, id_funcion, id_sala, capacidad):
        """Genera asientos para una función"""
        try:
            # Primero eliminar asientos existentes (si los hay)
            query_eliminar = "DELETE FROM asientos WHERE id_funcion = %s"
            self.db.ejecutar_consulta(query_eliminar, (id_funcion,))
            
            # Generar asientos (ejemplo: A1, A2, ..., B1, B2, ...)
            filas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            asientos_por_fila = (capacidad // len(filas)) + 1
            
            for fila in filas:
                for numero in range(1, asientos_por_fila + 1):
                    if len(filas) * (numero - 1) + filas.index(fila) + 1 > capacidad:
                        break
                    
                    numero_asiento = f"{fila}{numero}"
                    query_insert = """
                    INSERT INTO asientos (id_funcion, numero_asiento, estado)
                    VALUES (%s, %s, 'disponible')
                    """
                    self.db.ejecutar_consulta(query_insert, (id_funcion, numero_asiento))
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al generar asientos: {e}")
    
    def ocupar_asiento(self, id_asiento):
        """Marca un asiento como ocupado"""
        query = "UPDATE asientos SET estado = 'ocupado' WHERE id_asiento = %s"
        self.db.ejecutar_consulta(query, (id_asiento,))
        self.db.commit()
    
    def liberar_asiento(self, id_asiento):
        """Marca un asiento como disponible"""
        query = "UPDATE asientos SET estado = 'disponible' WHERE id_asiento = %s"
        self.db.ejecutar_consulta(query, (id_asiento,))
        self.db.commit()