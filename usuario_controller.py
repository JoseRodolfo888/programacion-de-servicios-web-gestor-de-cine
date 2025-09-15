from view.usuario_view import UsuarioView
from tkinter import messagebox

class UsuarioController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.usuario_view = UsuarioView(main_view)
    
    def mostrar_menu_usuario(self, usuario):
        """Muestra el menú de usuario"""
        self.usuario_view.mostrar_menu_usuario(usuario, self)
    
    def mostrar_cartelera(self):
        """Muestra la cartelera para usuarios"""
        from controller.pelicula_controller import PeliculaController
        PeliculaController(self.view, self.db_model).mostrar_cartelera()
    
    def comprar_boletos(self, usuario):
        """Inicia proceso de compra de boletos"""
        from controller.boleto_controller import BoletoController
        BoletoController(self.view, self.db_model).comprar_boletos(usuario)
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        self.view.mostrar_menu_principal(self.view.root)