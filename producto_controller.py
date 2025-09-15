from model.producto_model import ProductoModel
from view.producto_view import ProductoView
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

class ProductoController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.producto_model = ProductoModel(db_model)
        self.producto_view = ProductoView(main_view)
    
    def menu_gestion_productos(self):
        """Muestra el menú de gestión de productos"""
        self.producto_view.mostrar_menu_gestion_productos(self)
    
    def agregar_producto(self):
        """Muestra formulario para agregar producto"""
        entries = self.producto_view.mostrar_formulario_producto("AGREGAR PRODUCTO")
        
        # Botones
        button_frame = self.view.crear_frame_botones(self.view.content_frame)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=lambda: self.guardar_producto(entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.menu_gestion_productos).pack(side=tk.LEFT, padx=5)
    
    def guardar_producto(self, entries):
        """Guarda un nuevo producto"""
        nombre = entries['nombre'].get()
        precio = entries['precio'].get()
        stock = entries['stock'].get()
        
        # Validaciones
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío")
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
            stock = int(stock)
            if stock < 0:
                messagebox.showerror("Error", "El stock no puede ser negativo")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un stock válido")
            return
        
        try:
            self.producto_model.agregar_producto(nombre, precio, stock)
            messagebox.showinfo("Éxito", f"¡Producto '{nombre}' agregado exitosamente!")
            self.menu_gestion_productos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {e}")
    
    def mostrar_todos_productos(self):
        """Muestra todos los productos"""
        try:
            productos = self.producto_model.obtener_todos_productos()
            
            self.view.limpiar_contenido()
            ttk.Label(self.view.content_frame, text="LISTA DE PRODUCTOS", style='Header.TLabel').pack(pady=10)
            
            if not productos:
                ttk.Label(self.view.content_frame, text="No hay productos registrados.").pack()
                ttk.Button(self.view.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)
                return
            
            # Crear Treeview para mostrar la tabla
            tree_frame = ttk.Frame(self.view.content_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
            
            # Configurar columnas
            tree.heading("ID", text="ID")
            tree.heading("Nombre", text="Nombre")
            tree.heading("Precio", text="Precio")
            tree.heading("Stock", text="Stock")
            
            tree.column("ID", width=50, anchor="center")
            tree.column("Nombre", width=150)
            tree.column("Precio", width=80, anchor="center")
            tree.column("Stock", width=80, anchor="center")
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)
            
            # Insertar datos
            for producto in productos:
                stock = f"{producto['stock']} ✅" if producto['stock'] > 0 else f"{producto['stock']} ⚠️"
                tree.insert("", "end", values=(
                    producto['id_producto'],
                    producto['nombre'],
                    f"${producto['precio']:.2f}",
                    stock
                ))
            
            # Botón de regreso
            ttk.Button(self.view.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")