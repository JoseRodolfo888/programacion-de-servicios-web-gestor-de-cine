class PeliculaModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_todas_peliculas(self):
        """Obtiene todas las películas"""
        query = "SELECT * FROM peliculas ORDER BY titulo"
        return self.db.ejecutar_consulta(query).fetchall()
    
    def obtener_pelicula_por_id(self, id_pelicula):
        """Obtiene una película por su ID"""
        query = "SELECT * FROM peliculas WHERE id_pelicula = %s"
        return self.db.ejecutar_consulta(query, (id_pelicula,)).fetchone()
    
    def agregar_pelicula(self, titulo, director, duracion, clasificacion, genero):
        """Agrega una nueva película"""
        query = """
        INSERT INTO peliculas (titulo, director, duracion, clasificacion, genero)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.db.ejecutar_consulta(query, (titulo, director, duracion, clasificacion, genero))
        self.db.commit()
    
    def actualizar_pelicula(self, id_pelicula, titulo, director, duracion, clasificacion, genero):
        """Actualiza una película existente"""
        query = """
        UPDATE peliculas 
        SET titulo = %s, director = %s, duracion = %s, clasificacion = %s, genero = %s
        WHERE id_pelicula = %s
        """
        self.db.ejecutar_consulta(query, (titulo, director, duracion, clasificacion, genero, id_pelicula))
        self.db.commit()
    
    def eliminar_pelicula(self, id_pelicula):
        """Elimina una película y sus funciones relacionadas"""
        try:
            # Primero eliminar funciones relacionadas
            query_funciones = "DELETE FROM funciones WHERE id_pelicula = %s"
            self.db.ejecutar_consulta(query_funciones, (id_pelicula,))
            
            # Luego eliminar la película
            query_pelicula = "DELETE FROM peliculas WHERE id_pelicula = %s"
            self.db.ejecutar_consulta(query_pelicula, (id_pelicula,))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar película: {e}")
    
    def buscar_pelicula(self, termino):
        """Busca películas por título o género"""
        query = """
        SELECT * FROM peliculas 
        WHERE titulo LIKE %s OR genero LIKE %s
        ORDER BY titulo
        """
        return self.db.ejecutar_consulta(query, (f"%{termino}%", f"%{termino}%")).fetchall()
    
    def obtener_peliculas_con_funciones(self):
        """Obtiene películas que tienen funciones programadas"""
        query = """
        SELECT DISTINCT p.* 
        FROM peliculas p
        JOIN funciones f ON p.id_pelicula = f.id_pelicula
        WHERE f.horario > NOW()
        ORDER BY p.titulo
        """
        return self.db.ejecutar_consulta(query).fetchall()