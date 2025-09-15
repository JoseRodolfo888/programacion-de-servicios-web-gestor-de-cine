import tkinter
from model.pelicula_model import PeliculaModel
from model.funcion_model import FuncionModel
from view.pelicula_view import PeliculaView
from view.cartelera_view import CarteleraView
from view.admin_view import AdminView
from tkinter import Tk, messagebox, ttk
import tkinter as tk
class PeliculaController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.pelicula_model = PeliculaModel(db_model)
        self.funcion_model = FuncionModel(db_model)
        self.pelicula_view = PeliculaView(main_view)
        self.cartelera_view = CarteleraView(main_view)
        self.admin_view = AdminView(main_view)
    
    def mostrar_menu_administrador(self):
        """Muestra el menú de administrador"""
        self.admin_view.mostrar_menu_administrador(self)
    
    def menu_gestion_peliculas(self):
        """Muestra el menú de gestión de películas"""
        self.pelicula_view.mostrar_menu_gestion_peliculas(self)
    
    def mostrar_cartelera(self):
        """Muestra la cartelera de películas"""
        try:
            # Obtener funciones con información completa
            query = """
            SELECT p.titulo, p.director, p.duracion, p.clasificacion, p.genero, 
                   f.id_funcion, f.horario, s.nombre as sala, f.precio,
                   COUNT(a.id_asiento) as asientos_disponibles
            FROM peliculas p
            JOIN funciones f ON p.id_pelicula = f.id_pelicula
            JOIN salas s ON f.id_sala = s.id_sala
            LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
            WHERE f.horario > NOW()
            GROUP BY f.id_funcion
            ORDER BY f.horario
            """
            
            funciones = self.db_model.ejecutar_consulta(query).fetchall()
            self.cartelera_view.mostrar(funciones, self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar cartelera: {e}")
            self.view.mostrar_menu_principal(self.view.root)
    
    def agregar_pelicula(self):
        """Muestra formulario para agregar película"""
        entries = self.pelicula_view.mostrar_formulario_pelicula("AGREGAR PELÍCULA")
        
        # Botones
        button_frame = self.view.crear_frame_botones(self.view.content_frame)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=lambda: self.guardar_pelicula(entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.menu_gestion_peliculas).pack(side=tk.LEFT, padx=5)
    
    def guardar_pelicula(self, entries):
        """Guarda una nueva película"""
        titulo = entries['titulo'].get()
        director = entries['director'].get() or "Desconocido"
        duracion = entries['duracion'].get()
        clasificacion = entries['clasificacion'].get() or "NR"
        genero = entries['genero'].get() or "Otro"
        
        # Validaciones
        if not titulo.strip():
            messagebox.showerror("Error", "El título no puede estar vacío")
            return
        
        try:
            duracion = int(duracion)
            if duracion <= 0:
                messagebox.showerror("Error", "La duración debe ser mayor a 0 minutos")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la duración")
            return
        
        try:
            self.pelicula_model.agregar_pelicula(titulo, director, duracion, clasificacion, genero)
            messagebox.showinfo("Éxito", f"¡Película '{titulo}' agregada exitosamente!")
            self.menu_gestion_peliculas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar película: {e}")
    
    def editar_pelicula(self):
        """Muestra interfaz para editar película"""
        try:
            peliculas = self.pelicula_model.obtener_todas_peliculas()
            self.pelicula_view.mostrar_seleccion_pelicula(
                peliculas, "EDITAR PELÍCULA", self, "editar"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar películas: {e}")
    
    def ejecutar_accion_pelicula(self, seleccion, peliculas, accion):
        """Ejecuta acción sobre película seleccionada"""
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una película")
            return
        
        try:
            id_pelicula = int(seleccion.split(" - ")[0])
            pelicula = next((p for p in peliculas if p['id_pelicula'] == id_pelicula), None)
            
            if not pelicula:
                messagebox.showerror("Error", "Película no encontrada")
                return
            
            if accion == "editar":
                self.mostrar_formulario_edicion_pelicula(pelicula)
            elif accion == "eliminar":
                self.confirmar_eliminar_pelicula(pelicula)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar selección: {e}")
    
    def mostrar_formulario_edicion_pelicula(self, pelicula):
        """Muestra formulario para editar película"""
        valores = {
            'titulo': pelicula['titulo'],
            'director': pelicula['director'],
            'duracion': pelicula['duracion'],
            'clasificacion': pelicula['clasificacion'],
            'genero': pelicula['genero']
        }
        
        entries = self.pelicula_view.mostrar_formulario_pelicula(
            f"EDITAR PELÍCULA: {pelicula['titulo']}", valores
        )
        
        # Botones
        button_frame = self.view.crear_frame_botones(self.view.content_frame)
        
        ttk.Button(button_frame, text="Guardar cambios", 
                  command=lambda: self.guardar_cambios_pelicula(pelicula['id_pelicula'], entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.menu_gestion_peliculas).pack(side=tk.LEFT, padx=5)
    
    def guardar_cambios_pelicula(self, id_pelicula, entries):
        """Guarda los cambios de una película"""
        titulo = entries['titulo'].get()
        director = entries['director'].get()
        duracion = entries['duracion'].get()
        clasificacion = entries['clasificacion'].get()
        genero = entries['genero'].get()
        
        # Validaciones
        if not titulo.strip():
            messagebox.showerror("Error", "El título no puede estar vacío")
            return
        
        try:
            duracion = int(duracion)
            if duracion <= 0:
                messagebox.showerror("Error", "La duración debe ser mayor a 0 minutos")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la duración")
            return
        
        try:
            self.pelicula_model.actualizar_pelicula(
                id_pelicula, titulo, director, duracion, clasificacion, genero
            )
            messagebox.showinfo("Éxito", "¡Película actualizada exitosamente!")
            self.menu_gestion_peliculas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar película: {e}")
    
    def eliminar_pelicula(self):
        """Muestra interfaz para eliminar película"""
        try:
            peliculas = self.pelicula_model.obtener_todas_peliculas()
            self.pelicula_view.mostrar_seleccion_pelicula(
                peliculas, "ELIMINAR PELÍCULA", self, "eliminar"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar películas: {e}")
    
    def confirmar_eliminar_pelicula(self, pelicula):
        """Confirma la eliminación de una película"""
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro de eliminar la película '{pelicula['titulo']}'?\nEsta acción no se puede deshacer."
        )
        
        if confirmacion:
            try:
                if self.pelicula_model.eliminar_pelicula(pelicula['id_pelicula']):
                    messagebox.showinfo("Éxito", "¡Película eliminada exitosamente!")
                    self.menu_gestion_peliculas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar película: {e}")
    
    def mostrar_todas_peliculas(self):
        """Muestra todas las películas"""
        try:
            peliculas = self.pelicula_model.obtener_todas_peliculas()
            self.pelicula_view.mostrar_lista_peliculas(
                peliculas, "LISTA DE PELÍCULAS", self
            )
            
            # Botón de regreso
            ttk.Button(self.view.content_frame, text="Regresar", 
                      command=self.menu_gestion_peliculas).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar películas: {e}")
    
    def buscar_pelicula(self):
        """Muestra interfaz para buscar películas"""
        self.view.limpiar_contenido()
        
        ttk.Label(self.view.content_frame, text="BUSCAR PELÍCULA", style='Header.TLabel').pack(pady=10)
        
        ttk.Label(self.view.content_frame, text="Ingrese término de búsqueda (título o género):").pack()
        
        busqueda_entry = ttk.Entry(self.view.content_frame, width=30)
        busqueda_entry.pack(pady=10)
        
        ttk.Button(self.view.content_frame, text="Buscar", 
                  command=lambda: self.ejecutar_busqueda_pelicula(busqueda_entry.get())).pack(pady=5)
        ttk.Button(self.view.content_frame, text="Regresar", 
                  command=self.menu_gestion_peliculas).pack(pady=5)
    
    def ejecutar_busqueda_pelicula(self, termino):
        """Ejecuta la búsqueda de películas"""
        if not termino.strip():
            messagebox.showerror("Error", "Ingrese un término de búsqueda")
            return
        
        try:
            resultados = self.pelicula_model.buscar_pelicula(termino)
            
            if not resultados:
                messagebox.showinfo("Búsqueda", "No se encontraron películas con ese criterio")
                return
            
            self.pelicula_view.mostrar_lista_peliculas(
                resultados, f"RESULTADOS DE BÚSQUEDA: '{termino}'", self
            )
            
            # Botón de regreso
            ttk.Button(self.view.content_frame, text="Nueva búsqueda", 
                      command=self.buscar_pelicula).pack(side=Tk.LEFT, padx=5, pady=10)
            ttk.Button(self.view.content_frame, text="Regresar al menú", 
                      command=self.menu_gestion_peliculas).pack(side=tk.LEFT, padx=5, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar películas: {e}")