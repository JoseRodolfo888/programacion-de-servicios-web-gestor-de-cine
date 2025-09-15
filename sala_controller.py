from model.sala_model import SalaModel
from view.sala_view import SalaView
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

class SalaController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.sala_model = SalaModel(db_model)
        self.sala_view = SalaView(main_view)
    
    def menu_gestion_salas(self):
        """Muestra el menú de gestión de salas"""
        self.sala_view.mostrar_menu_gestion_salas(self)
    
    def agregar_sala(self):
        """Muestra formulario para agregar sala"""
        entries = self.sala_view.mostrar_formulario_sala("AGREGAR SALA")
        
        # Botones
        button_frame = self.view.crear_frame_botones(self.view.content_frame)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=lambda: self.guardar_sala(entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.menu_gestion_salas).pack(side=tk.LEFT, padx=5)
    
    def guardar_sala(self, entries):
        """Guarda una nueva sala"""
        nombre = entries['nombre'].get()
        capacidad = entries['capacidad'].get()
        
        # Validaciones
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        try:
            capacidad = int(capacidad)
            if capacidad <= 0:
                messagebox.showerror("Error", "La capacidad debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la capacidad")
            return
        
        try:
            self.sala_model.agregar_sala(nombre, capacidad)
            messagebox.showinfo("Éxito", f"¡Sala '{nombre}' agregada exitosamente!")
            self.menu_gestion_salas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar sala: {e}")
    
    def mostrar_todas_salas(self):
        """Muestra todas las salas"""
        try:
            salas = self.sala_model.obtener_todas_salas()
            self.sala_view.mostrar_lista_salas(
                salas, "LISTA DE SALAS", self
            )
            
            # Botón de regreso
            ttk.Button(self.view.content_frame, text="Regresar", 
                      command=self.menu_gestion_salas).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar salas: {e}")