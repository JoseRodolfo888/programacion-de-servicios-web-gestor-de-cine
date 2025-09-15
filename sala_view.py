import tkinter as tk
from tkinter import ttk

class SalaView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_gestion_salas(self, controlador):
        """Muestra el menú de gestión de salas"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="GESTIÓN DE SALAS", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar sala", controlador.agregar_sala),
            ("Editar sala", controlador.editar_sala),
            ("Eliminar sala", controlador.eliminar_sala),
            ("Ver todas las salas", controlador.mostrar_todas_salas),
            ("Cambiar estado de sala", controlador.cambiar_estado_sala),
            ("Regresar", controlador.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def mostrar_formulario_sala(self, titulo, valores=None):
        """Muestra formulario para agregar/editar sala"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        campos = [
            ("Nombre de la sala:", "nombre"),
            ("Capacidad de asientos:", "capacidad")
        ]
        
        entries = {}
        for texto, nombre in campos:
            ttk.Label(self.main_view.content_frame, text=texto).pack()
            entry = ttk.Entry(self.main_view.content_frame, width=30)
            if valores and nombre in valores:
                entry.insert(0, valores[nombre])
            entry.pack(pady=5)
            entries[nombre] = entry
        
        return entries
    
    def mostrar_lista_salas(self, salas, titulo, controlador):
        """Muestra lista de salas en una tabla"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        if not salas:
            ttk.Label(self.main_view.content_frame, text="No hay salas registradas.").pack()
            ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.menu_gestion_salas).pack(pady=10)
            return None
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.main_view.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Capacidad", "Estado"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Capacidad", text="Capacidad")
        tree.heading("Estado", text="Estado")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Nombre", width=150)
        tree.column("Capacidad", width=80, anchor="center")
        tree.column("Estado", width=120, anchor="center")
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for sala in salas:
            estado = "🟢 Disponible" if sala['estado'] == 'disponible' else "🔴 Mantenimiento"
            tree.insert("", "end", values=(
                sala['id_sala'],
                sala['nombre'],
                sala['capacidad'],
                estado
            ))
        
        return tree