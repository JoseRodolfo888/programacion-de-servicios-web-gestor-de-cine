import tkinter as tk
from tkinter import ttk

class UsuarioView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_usuario(self, usuario, controlador):
        """Muestra el menú de usuario"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=f"BIENVENIDO {usuario['nombre'].upper()}", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Ver cartelera", controlador.mostrar_cartelera),
            ("Comprar boletos", lambda: controlador.comprar_boletos(usuario)),
            ("Comprar productos", lambda: controlador.comprar_productos(usuario)),
            ("Ver mis boletos", lambda: controlador.mostrar_boletos_usuario(usuario['id_usuario'])),
            ("Solicitar devolución", lambda: controlador.solicitar_devolucion(usuario['id_usuario'])),
            ("Cerrar sesión", controlador.cerrar_sesion)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)