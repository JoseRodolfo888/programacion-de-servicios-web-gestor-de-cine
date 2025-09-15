from model.funcion_model import FuncionModel
from model.pelicula_model import PeliculaModel
from model.sala_model import SalaModel
from view.funcion_view import FuncionView
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class FuncionController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.funcion_model = FuncionModel(db_model)
        self.pelicula_model = PeliculaModel(db_model)
        self.sala_model = SalaModel(db_model)
        self.funcion_view = FuncionView(main_view)
    
    def menu_gestion_funciones(self):
        """Muestra el menú de gestión de funciones"""
        self.funcion_view.mostrar_menu_gestion_funciones(self)
    
    def agregar_funcion(self):
        """Muestra formulario para agregar función"""
        try:
            peliculas = self.pelicula_model.obtener_peliculas_con_funciones()
            salas = self.sala_model.obtener_salas_disponibles()
            
            if not peliculas:
                messagebox.showerror("Error", "No hay películas registradas. Primero agregue películas.")
                self.menu_gestion_funciones()
                return
            
            if not salas:
                messagebox.showerror("Error", "No hay salas disponibles. Active alguna sala primero.")
                self.menu_gestion_funciones()
                return
            
            pelicula_var, sala_var, entries = self.funcion_view.mostrar_formulario_funcion(
                "AGREGAR FUNCIÓN", peliculas, salas
            )
            
            # Botones
            button_frame = self.view.crear_frame_botones(self.view.content_frame)
            
            ttk.Button(button_frame, text="Guardar", 
                      command=lambda: self.guardar_funcion(pelicula_var, sala_var, entries)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancelar", 
                      command=self.menu_gestion_funciones).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
    
    def guardar_funcion(self, pelicula_var, sala_var, entries):
        """Guarda una nueva función"""
        pelicula_seleccionada = pelicula_var.get()
        sala_seleccionada = sala_var.get()
        fecha_hora = entries['fecha_hora'].get()
        precio = entries['precio'].get()
        
        # Validaciones
        if not pelicula_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una película")
            return
        
        if not sala_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una sala")
            return
        
        try:
            id_pelicula = int(pelicula_seleccionada.split(" - ")[0])
            id_sala = int(sala_seleccionada.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Selección no válida")
            return
        
        try:
            horario = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
            if horario <= datetime.now():
                messagebox.showerror("Error", "La función debe ser en el futuro")
                return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD HH:MM")
            return
        
        try:
            precio = float(precio)
            if precio < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un precio válido")
            return
        
        try:
            # Verificar disponibilidad de sala
            if not self.funcion_model.verificar_disponibilidad_sala(id_sala, horario):
                messagebox.showerror("Error", "La sala no está disponible en ese horario")
                return
            
            # Agregar función
            id_funcion = self.funcion_model.agregar_funcion(id_pelicula, id_sala, horario, precio)
            messagebox.showinfo("Éxito", "¡Función agregada exitosamente!")
            
            # Preguntar si desea generar asientos
            if messagebox.askyesno("Generar asientos", "¿Desea generar los asientos para esta función?"):
                from model.asiento_model import AsientoModel
                asiento_model = AsientoModel(self.db_model)
                sala = self.sala_model.obtener_sala_por_id(id_sala)
                asiento_model.generar_asientos(id_funcion, id_sala, sala['capacidad'])
                messagebox.showinfo("Éxito", "Asientos generados exitosamente")
            
            self.menu_gestion_funciones()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar función: {e}")