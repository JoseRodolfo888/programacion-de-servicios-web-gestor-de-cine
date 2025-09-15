from model.database_model import DatabaseModel
from view.main_view import MainView
from tkinter import messagebox
import sys
import os

# Añadir el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MainController:
    def __init__(self, root):
        self.view = MainView(root)
        self.db_model = DatabaseModel()
        self.auth_controller = None
        
        try:
            if self.db_model.conectar_bd():
                self.mostrar_menu_principal()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            root.destroy()
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal"""
        self.view.mostrar_menu_principal(self)
    
    def mostrar_login(self):
        """Muestra la interfaz de login"""
        if not self.auth_controller:
            from controller.auth_controller import AuthController
            self.auth_controller = AuthController(self.view, self.db_model, self)
        self.auth_controller.mostrar_login()
    
    def mostrar_registro(self):
        """Muestra la interfaz de registro"""
        if not self.auth_controller:
            from controller.auth_controller import AuthController
            self.auth_controller = AuthController(self.view, self.db_model, self)
        self.auth_controller.mostrar_registro()
    
    def mostrar_cartelera(self):
        """Muestra la cartelera de películas"""
        from controller.pelicula_controller import PeliculaController
        pelicula_controller = PeliculaController(self.view, self.db_model, self)
        pelicula_controller.mostrar_cartelera()
    
    def salir(self):
        """Cierra la aplicación"""
        self.db_model.desconectar_bd()
        self.view.root.destroy()