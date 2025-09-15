import tkinter as tk
from tkinter import ttk

class AdminView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_administrador(self, controlador):
        """Muestra el menú de administrador"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="PANEL DE ADMINISTRADOR", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Gestión de Películas", controlador.menu_gestion_peliculas),
            ("Gestión de Salas", controlador.menu_gestion_salas),
            ("Gestión de Funciones", controlador.menu_gestion_funciones),
            ("Gestión de Productos", controlador.menu_gestion_productos),
            ("Ver Reportes", controlador.mostrar_reportes),
            ("Cerrar sesión", controlador.cerrar_sesion)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)