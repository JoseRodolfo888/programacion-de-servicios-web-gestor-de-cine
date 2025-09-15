from model.funcion_model import FuncionModel
from model.asiento_model import AsientoModel
from model.boleto_model import BoletoModel
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

class BoletoController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.funcion_model = FuncionModel(db_model)
        self.asiento_model = AsientoModel(db_model)
        self.boleto_model = BoletoModel(db_model)
    
    def comprar_boletos(self, usuario):
        """Muestra interfaz para comprar boletos"""
        try:
            # Obtener funciones disponibles
            query = """
            SELECT f.id_funcion, p.titulo, f.horario, s.nombre as sala, f.precio,
                   COUNT(a.id_asiento) as asientos_disponibles
            FROM funciones f
            JOIN peliculas p ON f.id_pelicula = p.id_pelicula
            JOIN salas s ON f.id_sala = s.id_sala
            LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
            WHERE f.horario > NOW()
            GROUP BY f.id_funcion
            HAVING asientos_disponibles > 0
            ORDER BY f.horario
            """
            
            funciones = self.db_model.ejecutar_consulta(query).fetchall()
            
            if not funciones:
                messagebox.showinfo("Info", "No hay funciones con asientos disponibles en este momento.")
                return
            
            self.view.limpiar_contenido()
            ttk.Label(self.view.content_frame, text="COMPRA DE BOLETOS", style='Header.TLabel').pack(pady=10)
            
            ttk.Label(self.view.content_frame, text="Seleccione una función:").pack()
            
            funcion_var = tk.StringVar()
            funcion_combobox = ttk.Combobox(self.view.content_frame, textvariable=funcion_var, state="readonly")
            funcion_combobox['values'] = [f"{f['id_funcion']} - {f['titulo']} ({f['horario'].strftime('%d/%m/%Y %H:%M')})" for f in funciones]
            funcion_combobox.pack(pady=10)
            
            ttk.Button(self.view.content_frame, text="Continuar", 
                      command=lambda: self.seleccionar_asiento(usuario, funcion_var.get(), funciones)).pack(pady=5)
            ttk.Button(self.view.content_frame, text="Regresar", 
                      command=lambda: self.mostrar_menu_usuario(usuario)).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar funciones: {e}")
    
    def seleccionar_asiento(self, usuario, seleccion, funciones):
        """Muestra selección de asientos"""
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una función")
            return
        
        try:
            id_funcion = int(seleccion.split(" - ")[0])
            funcion = next((f for f in funciones if f['id_funcion'] == id_funcion), None)
            
            if not funcion:
                messagebox.showerror("Error", "Función no encontrada")
                return
            
            self.view.limpiar_contenido()
            ttk.Label(self.view.content_frame, text="SELECCIONAR ASIENTO", style='Header.TLabel').pack(pady=10)
            ttk.Label(self.view.content_frame, text=f"Película: {funcion['titulo']}").pack()
            ttk.Label(self.view.content_frame, text=f"Horario: {funcion['horario'].strftime('%d/%m/%Y %H:%M')}").pack()
            ttk.Label(self.view.content_frame, text=f"Sala: {funcion['sala']}").pack()
            ttk.Label(self.view.content_frame, text=f"Precio: ${funcion['precio']:.2f}").pack()
            
            # Obtener asientos disponibles
            asientos = self.asiento_model.obtener_asientos_disponibles(id_funcion)
            
            ttk.Label(self.view.content_frame, text="Asientos disponibles:").pack()
            
            asiento_var = tk.StringVar()
            asiento_combobox = ttk.Combobox(self.view.content_frame, textvariable=asiento_var, state="readonly")
            asiento_combobox['values'] = [a['numero_asiento'] for a in asientos]
            asiento_combobox.pack(pady=10)
            
            # Métodos de pago
            ttk.Label(self.view.content_frame, text="Método de pago:").pack()
            
            metodo_pago = tk.StringVar(value="tarjeta")
            metodos = [
                ("Tarjeta de crédito/débito", "tarjeta"),
                ("PayPal", "paypal"),
                ("Efectivo", "efectivo"),
                ("Criptomonedas", "cripto")
            ]
            
            for text, value in metodos:
                ttk.Radiobutton(self.view.content_frame, text=text, variable=metodo_pago, value=value).pack(anchor="w")
            
            # Botones
            button_frame = self.view.crear_frame_botones(self.view.content_frame)
            
            ttk.Button(button_frame, text="Comprar", 
                      command=lambda: self.procesar_compra(usuario, funcion, asiento_var.get(), metodo_pago.get(), asientos)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancelar", 
                      command=lambda: self.comprar_boletos(usuario)).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar asientos: {e}")
    
    def procesar_compra(self, usuario, funcion, numero_asiento, metodo_pago, asientos):
        """Procesa la compra del boleto"""
        if not numero_asiento:
            messagebox.showerror("Error", "Debe seleccionar un asiento")
            return
        
        # Verificar si el asiento existe y está disponible
        asiento = next((a for a in asientos if a['numero_asiento'] == numero_asiento), None)
        
        if not asiento:
            messagebox.showerror("Error", "Asiento no disponible o no válido")
            return
        
        try:
            # Insertar boleto
            id_boleto = self.boleto_model.comprar_boleto(usuario['id_usuario'], funcion['id_funcion'], asiento['id_asiento'])
            
            # Ocupar asiento
            self.asiento_model.ocupar_asiento(asiento['id_asiento'])
            
            # Registrar pago
            query_pago = """
            INSERT INTO pagos (id_boleto, metodo, estado)
            VALUES (%s, %s, 'completado')
            """
            self.db_model.ejecutar_consulta(query_pago, (id_boleto, metodo_pago))
            self.db_model.commit()
            
            # Mostrar resumen de compra
            resumen = f"""
            ¡Compra exitosa! Disfrute de {funcion['titulo']}.
            
            Fecha: {funcion['horario'].strftime('%d/%m/%Y %H:%M')}
            Sala: {funcion['sala']}
            Asiento: {numero_asiento}
            Precio: ${funcion['precio']:.2f}
            Método de pago: {metodo_pago.capitalize()}
            """
            
            messagebox.showinfo("Éxito", resumen)
            
            # Volver al menú de usuario
            from controller.usuario_controller import UsuarioController
            UsuarioController(self.view, self.db_model).mostrar_menu_usuario(usuario)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la compra: {e}")