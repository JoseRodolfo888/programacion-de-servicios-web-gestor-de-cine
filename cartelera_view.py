import tkinter as tk
from tkinter import ttk

class CarteleraView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar(self, funciones, controlador):
        """Muestra la cartelera de películas"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="CARTELERA", style='Header.TLabel').pack(pady=10)
        
        if not funciones:
            ttk.Label(self.main_view.content_frame, text="No hay funciones disponibles en este momento.").pack()
            ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.mostrar_menu_principal).pack(pady=10)
            return None
        
        # Crear frame con scroll
        canvas, scrollbar, scrollable_frame = self.main_view.crear_frame_con_scroll()
        
        # Mostrar cada función
        for funcion in funciones:
            frame_funcion = ttk.Frame(scrollable_frame, borderwidth=2, relief="groove", padding=10)
            frame_funcion.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(frame_funcion, text=f"🎞️ {funcion['titulo']}", font=('Arial', 11, 'bold')).pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Director: {funcion['director']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Duración: {funcion['duracion']} minutos").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Clasificación: {funcion['clasificacion']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Género: {funcion['genero']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Horario: {funcion['horario'].strftime('%d/%m/%Y %H:%M')}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Sala: {funcion['sala']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Precio: ${funcion['precio']:.2f}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Asientos disponibles: {funcion['asientos_disponibles']}").pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón de regreso
        ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.mostrar_menu_principal).pack(pady=10)
        
        return scrollable_frame