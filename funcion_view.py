import tkinter as tk
from tkinter import ttk

class FuncionView:
    def __init__(self, main_view):
        self.main_view = main_view
    
    def mostrar_menu_gestion_funciones(self, controlador):
        """Muestra el menú de gestión de funciones"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text="GESTIÓN DE FUNCIONES", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar función", controlador.agregar_funcion),
            ("Editar función", controlador.editar_funcion),
            ("Eliminar función", controlador.eliminar_funcion),
            ("Ver todas las funciones", controlador.mostrar_todas_funciones),
            ("Generar asientos para función", controlador.generar_asientos_funcion),
            ("Regresar", controlador.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_view.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def mostrar_formulario_funcion(self, titulo, peliculas, salas, valores=None):
        """Muestra formulario para agregar/editar función"""
        self.main_view.limpiar_contenido()
        
        ttk.Label(self.main_view.content_frame, text=titulo, style='Header.TLabel').pack(pady=10)
        
        # Selector de película
        ttk.Label(self.main_view.content_frame, text="Película:").pack()
        pelicula_var = tk.StringVar()
        pelicula_combobox = ttk.Combobox(self.main_view.content_frame, textvariable=pelicula_var, state="readonly")
        pelicula_combobox['values'] = [f"{p['id_pelicula']} - {p['titulo']}" for p in peliculas]
        if valores and 'id_pelicula' in valores:
            pelicula_texto = f"{valores['id_pelicula']} - {valores['titulo']}"
            pelicula_var.set(pelicula_texto)
        pelicula_combobox.pack(pady=5)
        
        # Selector de sala
        ttk.Label(self.main_view.content_frame, text="Sala:").pack()
        sala_var = tk.StringVar()
        sala_combobox = ttk.Combobox(self.main_view.content_frame, textvariable=sala_var, state="readonly")
        sala_combobox['values'] = [f"{s['id_sala']} - {s['nombre']}" for s in salas]
        if valores and 'id_sala' in valores:
            sala_texto = f"{valores['id_sala']} - {valores['sala_nombre']}"
            sala_var.set(sala_texto)
        sala_combobox.pack(pady=5)
        
        # Campos de entrada
        campos = [
            ("Fecha y hora (YYYY-MM-DD HH:MM):", "fecha_hora"),
            ("Precio del boleto:", "precio")
        ]
        
        entries = {}
        for texto, nombre in campos:
            ttk.Label(self.main_view.content_frame, text=texto).pack()
            entry = ttk.Entry(self.main_view.content_frame, width=30)
            if valores and nombre in valores:
                if nombre == 'fecha_hora' and 'horario' in valores:
                    entry.insert(0, valores['horario'].strftime('%Y-%m-%d %H:%M'))
                elif nombre == 'precio' and 'precio' in valores:
                    entry.insert(0, str(valores['precio']))
            entry.pack(pady=5)
            entries[nombre] = entry
        
        return pelicula_var, sala_var, entries