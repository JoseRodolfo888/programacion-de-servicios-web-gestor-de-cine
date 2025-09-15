import tkinter as tk
from tkinter import ttk

class ProductoView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_gestion_productos(self, controlador):
        """Muestra el menú de gestión de productos"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="GESTIÓN DE PRODUCTOS", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar producto", controlador.agregar_producto),
            ("Editar producto", controlador.editar_producto),
            ("Eliminar producto", controlador.eliminar_producto),
            ("Ver todos los productos", controlador.mostrar_todos_productos),
            ("Registrar entrada/salida", controlador.registrar_movimiento_inventario),
            ("Ver movimientos", controlador.mostrar_movimientos_inventario),
            ("Regresar", controlador.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def mostrar_formulario_producto(self, titulo, valores=None):
        """Muestra formulario para agregar/editar producto"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        campos = [
            ("Nombre del producto:", "nombre"),
            ("Precio unitario:", "precio")
        ]
        
        entries = {}
        for texto, nombre in campos:
            ttk.Label(self.main_view.content_frame, text=texto).pack()
            entry = ttk.Entry(self.main_view.content_frame, width=30)
            if valores and nombre in valores:
                entry.insert(0, valores[nombre])
            entry.pack(pady=5)
            entries[nombre] = entry
        
        # Para agregar, mostrar campo de stock
        if not valores:
            ttk.Label(self.main_view.content_frame, text="Stock inicial:").pack()
            stock_entry = ttk.Entry(self.main_view.content_frame, width=30)
            stock_entry.pack(pady=5)
            entries['stock'] = stock_entry
        
        return entries