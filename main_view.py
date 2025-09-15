import tkinter as tk
from tkinter import ttk

class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("CineMagic Premium - Sistema de Gestión")
        self.root.geometry("1000x700")
        
        # Configuración de estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Titulo.TLabel', font=('Arial', 14, 'bold'))
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de título
        self.crear_barra_titulo()
        
        # Frame de contenido
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def crear_barra_titulo(self):
        """Crea la barra de título de la aplicación"""
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(title_frame, text="・.・CineMagic Premium ・.・", style='Titulo.TLabel').pack()
        ttk.Label(title_frame, text="Sistema de Gestión Cinematográfica Completo").pack()
        ttk.Label(title_frame, text="Versión 3.0 - Panel Administrativo y Cliente").pack()
    
    def limpiar_contenido(self):
        """Limpia el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def mostrar_menu_principal(self, controlador):
        """Muestra el menú principal"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="MENÚ PRINCIPAL", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Iniciar sesión", controlador.mostrar_login),
            ("Registrarse", controlador.mostrar_registro),
            ("Ver cartelera", controlador.mostrar_cartelera),
            ("Salir", controlador.salir)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=20).pack(pady=5)
    
    def crear_frame_con_scroll(self):
        """Crea un frame con scrollbar"""
        # Crear canvas y scrollbar
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        
        # Frame scrollable
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        return canvas, scrollbar, scrollable_frame
    
    def crear_frame_botones(self, parent):
        """Crea un frame para botones"""
        frame = ttk.Frame(parent)
        frame.pack(pady=10)
        return frame
    
    def mostrar_mensaje(self, titulo, mensaje, tipo="info"):
        """Muestra un mensaje emergente"""
        from tkinter import messagebox
        if tipo == "info":
            messagebox.showinfo(titulo, mensaje)
        elif tipo == "error":
            messagebox.showerror(titulo, mensaje)
        elif tipo == "warning":
            messagebox.showwarning(titulo, mensaje)