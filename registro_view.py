import tkinter as tk
from tkinter import ttk

class RegistroView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar(self, controlador):
        """Muestra la interfaz de registro"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="REGISTRO DE USUARIO", style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        campos = [
            ("Nombre completo:", "nombre"),
            ("Edad:", "edad"),
            ("Correo electrónico:", "correo"),
            ("Contraseña (mínimo 6 caracteres):", "contraseña")
        ]
        
        entries = {}
        for texto, nombre in campos:
            ttk.Label(self.main_view.content_frame, text=texto).pack()
            entry = ttk.Entry(self.main_view.content_frame, width=30)
            if "contraseña" in nombre:
                entry.config(show="*")
            entry.pack(pady=5)
            entries[nombre] = entry
        
        # Botones
        button_frame = self.main_view.crear_frame_botones(self.main_view.content_frame)
        
        ttk.Button(button_frame, text="Registrarse", 
                  command=lambda: controlador.procesar_registro(
                      entries['nombre'].get(),
                      entries['edad'].get(),
                      entries['correo'].get(),
                      entries['contraseña'].get()
                  )).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Regresar", 
                  command=controlador.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
        
        return entries