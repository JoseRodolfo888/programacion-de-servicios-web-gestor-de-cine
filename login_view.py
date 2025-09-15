import tkinter as tk
from tkinter import ttk

class LoginView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar(self, controlador):
        """Muestra la interfaz de login"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="INICIO DE SESIÓN", style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        ttk.Label(self.main_view.content_frame, text="Correo electrónico:").pack()
        correo_entry = ttk.Entry(self.main_view.content_frame, width=30)
        correo_entry.pack(pady=5)
        
        ttk.Label(self.main_view.content_frame, text="Contraseña:").pack()
        contraseña_entry = ttk.Entry(self.main_view.content_frame, width=30, show="*")
        contraseña_entry.pack(pady=5)
        
        # Botones
        button_frame = self.main_view.crear_frame_botones(self.main_view.content_frame)
        
        ttk.Button(button_frame, text="Iniciar sesión", 
                  command=lambda: controlador.validar_login(correo_entry.get(), contraseña_entry.get())).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Regresar", 
                  command=controlador.cerrar_sesion).pack(side=tk.LEFT, padx=5)
        
        return correo_entry, contraseña_entry, button_frame