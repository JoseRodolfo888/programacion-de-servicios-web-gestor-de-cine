class UsuarioModel:
    def __init__(self, db_model):
        self.db = db_model
    
    def obtener_usuario_por_credenciales(self, correo, contraseña):
        """Obtiene un usuario por sus credenciales"""
        query = """
        SELECT u.*, r.nombre as rol 
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.correo = %s AND u.contraseña = %s
        """
        return self.db.ejecutar_consulta(query, (correo, contraseña)).fetchone()
    
    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene un usuario por su ID"""
        query = "SELECT * FROM usuarios WHERE id_usuario = %s"
        return self.db.ejecutar_consulta(query, (id_usuario,)).fetchone()
    
    def verificar_correo_existente(self, correo):
        """Verifica si un correo ya está registrado"""
        query = "SELECT COUNT(*) as existe FROM usuarios WHERE correo = %s"
        resultado = self.db.ejecutar_consulta(query, (correo,)).fetchone()
        return resultado['existe'] > 0
    
    def registrar_usuario(self, nombre, edad, correo, contraseña, id_rol=2):
        """Registra un nuevo usuario"""
        query = "INSERT INTO usuarios (nombre, edad, correo, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s)"
        self.db.ejecutar_consulta(query, (nombre, edad, correo, contraseña, id_rol))
        self.db.commit()
        return self.db.obtener_ultimo_id()
    
    def actualizar_usuario(self, id_usuario, nombre, edad, correo):
        """Actualiza un usuario existente"""
        query = "UPDATE usuarios SET nombre = %s, edad = %s, correo = %s WHERE id_usuario = %s"
        self.db.ejecutar_consulta(query, (nombre, edad, correo, id_usuario))
        self.db.commit()
    
    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario y sus boletos relacionados"""
        try:
            # Primero eliminar boletos relacionados
            query_boletos = "DELETE FROM boletos WHERE id_usuario = %s"
            self.db.ejecutar_consulta(query_boletos, (id_usuario,))
            
            # Luego eliminar el usuario
            query_usuario = "DELETE FROM usuarios WHERE id_usuario = %s"
            self.db.ejecutar_consulta(query_usuario, (id_usuario,))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar usuario: {e}")