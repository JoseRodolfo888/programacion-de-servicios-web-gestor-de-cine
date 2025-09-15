import tkinter as tk
from tkinter import ttk

class ReportesView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_reportes(self, controlador):
        """Muestra el menú de reportes"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="REPORTES", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Ventas por película", controlador.reporte_ventas_pelicula),
            ("Asistencia por función", controlador.reporte_asistencia_funcion),
            ("Productos más vendidos", controlador.reporte_productos_vendidos),
            ("Ingresos totales", controlador.reporte_ingresos_totales),
            ("Regresar", controlador.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def mostrar_reporte(self, datos, titulo, columnas, controlador):
        """Muestra un reporte en formato de tabla"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        if not datos:
            ttk.Label(self.main_view.content_frame, text="No hay datos para mostrar.").pack()
            ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.mostrar_reportes).pack(pady=10)
            return None
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.main_view.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=columnas, show="headings")
        
        # Configurar columnas
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for fila in datos:
            tree.insert("", "end", values=tuple(fila.values()))
        
        # Botón de regreso
        ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.mostrar_reportes).pack(pady=10)
        
        return tree