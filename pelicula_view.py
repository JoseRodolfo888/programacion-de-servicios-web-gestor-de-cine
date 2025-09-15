import tkinter as tk
from tkinter import ttk

class PeliculaView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_gestion_peliculas(self, controlador):
        """Muestra el menú de gestión de películas"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="GESTIÓN DE PELÍCULAS", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar película", controlador.agregar_pelicula),
            ("Editar película", controlador.editar_pelicula),
            ("Eliminar película", controlador.eliminar_pelicula),
            ("Ver todas las películas", controlador.mostrar_todas_peliculas),
            ("Buscar película", controlador.buscar_pelicula),
            ("Regresar", controlador.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def mostrar_formulario_pelicula(self, titulo, valores=None):
        """Muestra formulario para agregar/editar película"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        campos = [
            ("Título de la película:", "titulo"),
            ("Director:", "director"),
            ("Duración (minutos):", "duracion"),
            ("Clasificación (ej. 'A', 'B', 'PG-13'):", "clasificacion"),
            ("Género:", "genero")
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
    
    def mostrar_lista_peliculas(self, peliculas, titulo, controlador):
        """Muestra lista de películas en una tabla"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        if not peliculas:
            ttk.Label(self.main_view.content_frame, text="No hay películas registradas.").pack()
            ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.menu_gestion_peliculas).pack(pady=10)
            return None
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.main_view.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Título", "Director", "Duración", "Clasificación", "Género"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Título", text="Título")
        tree.heading("Director", text="Director")
        tree.heading("Duración", text="Duración")
        tree.heading("Clasificación", text="Clasificación")
        tree.heading("Género", text="Género")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Título", width=150)
        tree.column("Director", width=120)
        tree.column("Duración", width=80, anchor="center")
        tree.column("Clasificación", width=80, anchor="center")
        tree.column("Género", width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for pelicula in peliculas:
            tree.insert("", "end", values=(
                pelicula['id_pelicula'],
                pelicula['titulo'],
                pelicula['director'],
                f"{pelicula['duracion']} min",
                pelicula['clasificacion'],
                pelicula['genero']
            ))
        
        return tree
    
    def mostrar_seleccion_pelicula(self, peliculas, titulo, controlador, accion):
        """Muestra selector de película para editar/eliminar"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        if not peliculas:
            ttk.Label(self.main_view.content_frame, text="No hay películas registradas.").pack()
            ttk.Button(self.main_view.content_frame, text="Regresar", command=controlador.menu_gestion_peliculas).pack(pady=10)
            return None
        
        ttk.Label(self.main_view.content_frame, text="Seleccione la película:").pack()
        
        pelicula_var = tk.StringVar()
        pelicula_combobox = ttk.Combobox(self.main_view.content_frame, textvariable=pelicula_var, state="readonly")
        pelicula_combobox['values'] = [f"{p['id_pelicula']} - {p['titulo']}" for p in peliculas]
        pelicula_combobox.pack(pady=10)
        
        ttk.Button(self.main_view.content_frame, text="Seleccionar", 
                  command=lambda: controlador.ejecutar_accion_pelicula(pelicula_var.get(), peliculas, accion)).pack(pady=5)
        ttk.Button(self.main_view.content_frame, text="Regresar", 
                  command=controlador.menu_gestion_peliculas).pack(pady=5)
        
        return pelicula_var