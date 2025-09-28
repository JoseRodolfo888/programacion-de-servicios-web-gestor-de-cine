import mysql.connector
from mysql.connector import pooling
import os
from typing import Optional, Dict, Any
import logging
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexiones a la base de datos con pool de conexiones"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'cine_user'),
            'password': os.getenv('DB_PASSWORD', 'cine_pass'),
            'database': os.getenv('DB_NAME', 'cine'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,
            'pool_name': 'cine_pool',
            'pool_size': 10,
            'pool_reset_session': True
        }

        retries = 5
        delay = 5
        for i in range(retries):
            try:
                self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.config)
                logger.info("Pool de conexiones creado exitosamente")
                return
            except mysql.connector.Error as err:
                logger.error(f"Error al crear pool de conexiones: {err}. Reintentando en {delay} segundos... (Intento {i+1}/{retries})")
                time.sleep(delay)
        
        logger.critical("No se pudo conectar a la base de datos después de varios intentos.")
        raise Exception("Fallo al conectar con la base de datos.")
    
    def get_connection(self):
        """Obtener conexión del pool"""
        try:
            return self.pool.get_connection()
        except mysql.connector.Error as err:
            logger.error(f"Error al obtener conexión: {err}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Ejecutar query con manejo de errores"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            query_type = query.strip().upper().split()[0]

            cursor.execute(query, params or ())
            
            if query_type == 'SELECT':
                return cursor.fetchall()
            elif query_type in ('INSERT', 'UPDATE', 'DELETE'):
                connection.commit()
                if query_type == 'INSERT' and not fetch:
                    return cursor.lastrowid
                return cursor.rowcount
            else:
                connection.commit()
                return None 
                
        except mysql.connector.Error as err:
            logger.error(f"Error ejecutando query: {err}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_many(self, query: str, params_list: list):
        """Ejecutar múltiples queries en una transacción"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error ejecutando queries múltiples: {err}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
