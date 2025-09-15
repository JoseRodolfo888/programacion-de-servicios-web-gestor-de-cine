import mysql.connector
from tkinter import messagebox
import os

class DatabaseModel:
    def conectar_bd(self):
        try:
            # Obtener variables de entorno para Docker
            host = os.getenv('MYSQL_HOST', 'localhost')
            user = os.getenv('MYSQL_USER', 'root')
            password = os.getenv('MYSQL_PASSWORD', '123456')
            database = os.getenv('MYSQL_DATABASE', 'cine')
            
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al conectar a la base de datos: {err}")
            return False