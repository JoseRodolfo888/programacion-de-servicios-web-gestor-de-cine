from datetime import datetime, timedelta

class FuncionModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_todas_funciones(self):
        """Obtiene todas las funciones"""
        query = """
        SELECT f.*, p.titulo, s.nombre as sala_nombre
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        ORDER BY f.horario
        """
        return self.db.ejecutar_consulta(query).fetchall()
    
    def obtener_funciones_futuras(self):
        """Obtiene funciones programadas para el futuro"""
        query = """
        SELECT f.*, p.titulo, s.nombre as sala_nombre
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        WHERE f.horario > NOW()
        ORDER BY f.horario
        """
        return self.db.ejecutar_consulta(query).fetchall()
    
    def obtener_funcion_por_id(self, id_funcion):
        """Obtiene una función por su ID"""
        query = """
        SELECT f.*, p.titulo, s.nombre as sala_nombre
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        WHERE f.id_funcion = %s
        """
        return self.db.ejecutar_consulta(query, (id_funcion,)).fetchone()
    
    def agregar_funcion(self, id_pelicula, id_sala, horario, precio):
        """Agrega una nueva función"""
        query = """
        INSERT INTO funciones (id_pelicula, id_sala, horario, precio)
        VALUES (%s, %s, %s, %s)
        """
        self.db.ejecutar_consulta(query, (id_pelicula, id_sala, horario, precio))
        self.db.commit()
        return self.db.obtener_ultimo_id()
    
    def actualizar_funcion(self, id_funcion, id_pelicula, id_sala, horario, precio):
        """Actualiza una función existente"""
        query = """
        UPDATE funciones 
        SET id_pelicula = %s, id_sala = %s, horario = %s, precio = %s
        WHERE id_funcion = %s
        """
        self.db.ejecutar_consulta(query, (id_pelicula, id_sala, horario, precio, id_funcion))
        self.db.commit()
    
    def eliminar_funcion(self, id_funcion):
        """Elimina una función y sus asientos relacionados"""
        try:
            # Primero eliminar asientos relacionados
            query_asientos = "DELETE FROM asientos WHERE id_funcion = %s"
            self.db.ejecutar_consulta(query_asientos, (id_funcion,))
            
            # Luego eliminar la función
            query_funcion = "DELETE FROM funciones WHERE id_funcion = %s"
            self.db.ejecutar_consulta(query_funcion, (id_funcion,))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar función: {e}")
    
    def obtener_funciones_por_pelicula(self, id_pelicula):
        """Obtiene funciones de una película específica"""
        query = """
        SELECT f.*, s.nombre as sala_nombre
        FROM funciones f
        JOIN salas s ON f.id_sala = s.id_sala
        WHERE f.id_pelicula = %s AND f.horario > NOW()
        ORDER BY f.horario
        """
        return self.db.ejecutar_consulta(query, (id_pelicula,)).fetchall()
    
    def verificar_disponibilidad_sala(self, id_sala, horario, duracion_minutos=120):
        """Verifica si una sala está disponible en un horario específico"""
        # Calcular hora de fin aproximada (horario + duración de la película)
        horario_fin = horario + timedelta(minutes=duracion_minutos)
        
        query = """
        SELECT COUNT(*) as conflicto
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        WHERE f.id_sala = %s AND (
            (f.horario <= %s AND DATE_ADD(f.horario, INTERVAL p.duracion MINUTE) >= %s) OR
            (f.horario <= %s AND DATE_ADD(f.horario, INTERVAL p.duracion MINUTE) >= %s) OR
            (f.horario >= %s AND DATE_ADD(f.horario, INTERVAL p.duracion MINUTE) <= %s)
        )
        """
        resultado = self.db.ejecutar_consulta(query, (
            id_sala, horario, horario, horario_fin, horario_fin, horario, horario_fin
        )).fetchone()
        
        return resultado['conflicto'] == 0