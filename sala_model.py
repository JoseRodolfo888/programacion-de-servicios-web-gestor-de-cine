class SalaModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_todas_salas(self):
        """Obtiene todas las salas"""
        query = "SELECT * FROM salas ORDER BY nombre"
        return self.db.ejecutar_consulta(query).fetchall()
    
    def obtener_sala_por_id(self, id_sala):
        """Obtiene una sala por su ID"""
        query = "SELECT * FROM salas WHERE id_sala = %s"
        return self.db.ejecutar_consulta(query, (id_sala,)).fetchone()
    
    def obtener_salas_disponibles(self):
        """Obtiene salas disponibles (no en mantenimiento)"""
        query = "SELECT * FROM salas WHERE estado = 'disponible' ORDER BY nombre"
        return self.db.ejecutar_consulta(query).fetchall()
    
    def agregar_sala(self, nombre, capacidad):
        """Agrega una nueva sala"""
        query = "INSERT INTO salas (nombre, capacidad) VALUES (%s, %s)"
        self.db.ejecutar_consulta(query, (nombre, capacidad))
        self.db.commit()
    
    def actualizar_sala(self, id_sala, nombre, capacidad):
        """Actualiza una sala existente"""
        query = "UPDATE salas SET nombre = %s, capacidad = %s WHERE id_sala = %s"
        self.db.ejecutar_consulta(query, (nombre, capacidad, id_sala))
        self.db.commit()
    
    def eliminar_sala(self, id_sala):
        """Elimina una sala y sus funciones relacionadas"""
        try:
            # Primero eliminar funciones relacionadas
            query_funciones = "DELETE FROM funciones WHERE id_sala = %s"
            self.db.ejecutar_consulta(query_funciones, (id_sala,))
            
            # Luego eliminar la sala
            query_sala = "DELETE FROM salas WHERE id_sala = %s"
            self.db.ejecutar_consulta(query_sala, (id_sala,))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar sala: {e}")
    
    def cambiar_estado_sala(self, id_sala, estado):
        """Cambia el estado de una sala (disponible/mantenimiento)"""
        query = "UPDATE salas SET estado = %s WHERE id_sala = %s"
        self.db.ejecutar_consulta(query, (estado, id_sala))
        self.db.commit()