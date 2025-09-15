class BoletoModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_boletos_por_usuario(self, id_usuario):
        """Obtiene los boletos de un usuario"""
        query = """
        SELECT b.*, p.titulo, f.horario, s.nombre as sala, a.numero_asiento
        FROM boletos b
        JOIN funciones f ON b.id_funcion = f.id_funcion
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        JOIN asientos a ON b.id_asiento = a.id_asiento
        WHERE b.id_usuario = %s
        ORDER BY f.horario DESC
        """
        return self.db.ejecutar_consulta(query, (id_usuario,)).fetchall()
    
    def comprar_boleto(self, id_usuario, id_funcion, id_asiento):
        """Compra un boleto"""
        query = "INSERT INTO boletos (id_usuario, id_funcion, id_asiento) VALUES (%s, %s, %s)"
        self.db.ejecutar_consulta(query, (id_usuario, id_funcion, id_asiento))
        self.db.commit()
        return self.db.obtener_ultimo_id()
    
    def obtener_boleto_por_id(self, id_boleto):
        """Obtiene un boleto por su ID"""
        query = """
        SELECT b.*, p.titulo, f.horario, s.nombre as sala, a.numero_asiento, u.nombre as usuario
        FROM boletos b
        JOIN funciones f ON b.id_funcion = f.id_funcion
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        JOIN asientos a ON b.id_asiento = a.id_asiento
        JOIN usuarios u ON b.id_usuario = u.id_usuario
        WHERE b.id_boleto = %s
        """
        return self.db.ejecutar_consulta(query, (id_boleto,)).fetchone()
    
    def cancelar_boleto(self, id_boleto):
        """Cancela un boleto"""
        try:
            # Primero liberar el asiento
            query_asiento = """
            UPDATE asientos SET estado = 'disponible' 
            WHERE id_asiento = (
                SELECT id_asiento FROM boletos WHERE id_boleto = %s
            )
            """
            self.db.ejecutar_consulta(query_asiento, (id_boleto,))
            
            # Luego eliminar el boleto
            query_boleto = "DELETE FROM boletos WHERE id_boleto = %s"
            self.db.ejecutar_consulta(query_boleto, (id_boleto,))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al cancelar boleto: {e}")