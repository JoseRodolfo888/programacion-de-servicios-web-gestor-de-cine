# Archivo de inicialización del módulo controller
from .main_controller import MainController
from .auth_controller import AuthController
from .pelicula_controller import PeliculaController
from .sala_controller import SalaController
from .funcion_controller import FuncionController
from .producto_controller import ProductoController
from .usuario_controller import UsuarioController
from .boleto_controller import BoletoController
from .reportes_controller import ReportesController

__all__ = [
    'MainController',
    'AuthController',
    'PeliculaController',
    'SalaController',
    'FuncionController',
    'ProductoController',
    'UsuarioController',
    'BoletoController',
    'ReportesController'
]