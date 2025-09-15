from model.usuario_model import UsuarioModel
from view.login_view import LoginView
from view.registro_view import RegistroView
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

class AuthController:
    def __init__(self, main_view, db_model, main_controller):
        self.view = main_view
        self.db_model = db_model
        self.main_controller = main_controller  # Referencia directa al MainController
        self.usuario_model = UsuarioModel(db_model)
        self.login_view = LoginView(main_view)
        self.registro_view = RegistroView(main_view)
    
    def mostrar_login(self):
        """Muestra la interfaz de login"""
        self.login_view.mostrar(self)
    
    def mostrar_registro(self):
        """Muestra la interfaz de registro"""
        self.registro_view.mostrar(self)
    
    def validar_login(self, correo, contraseña):
        """Valida las credenciales del usuario"""
        if not correo or not contraseña:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        try:
            usuario = self.usuario_model.obtener_usuario_por_credenciales(correo, contraseña)
            
            if usuario:
                messagebox.showinfo("Bienvenido", f"¡Bienvenido/a, {usuario['nombre']} ({usuario['rol']})!")
                self.redirigir_segun_rol(usuario)
            else:
                messagebox.showerror("Error", "Credenciales incorrectas. Intente nuevamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al validar credenciales: {e}")
    
    def redirigir_segun_rol(self, usuario):
        """Redirige al usuario según su rol"""
        if usuario['id_rol'] == 1:  # Administrador
            from controller.pelicula_controller import PeliculaController
            pelicula_controller = PeliculaController(self.view, self.db_model, self.main_controller)
            pelicula_controller.mostrar_menu_administrador()
        else:
            from controller.usuario_controller import UsuarioController
            usuario_controller = UsuarioController(self.view, self.db_model, self.main_controller)
            usuario_controller.mostrar_menu_usuario(usuario)
    
    def procesar_registro(self, nombre, edad, correo, contraseña):
        """Procesa el registro de un nuevo usuario"""
        # Validaciones
        if not all([nombre.strip(), edad, correo, contraseña]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            edad = int(edad)
            if not (5 <= edad <= 100):
                messagebox.showerror("Error", "La edad debe estar entre 5 y 100 años")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese una edad válida")
            return
        
        if "@" not in correo or "." not in correo:
            messagebox.showerror("Error", "Ingrese un correo válido")
            return
        
        if len(contraseña) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
            return
        
        try:
            # Verificar si el correo ya existe
            if self.usuario_model.verificar_correo_existente(correo):
                messagebox.showerror("Error", "El correo electrónico ya está registrado")
                return
            
            # Registrar usuario
            self.usuario_model.registrar_usuario(nombre, edad, correo, contraseña)
            messagebox.showinfo("Éxito", "¡Registro exitoso! Ahora puede iniciar sesión.")
            
            # Volver al menú principal
            self.main_controller.mostrar_menu_principal()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar usuario: {e}")
    
    def cerrar_sesion(self):
        """Cierra la sesión y vuelve al menú principal"""
        self.main_controller.mostrar_menu_principal()