from view.reportes_view import ReportesView
from tkinter import messagebox
from datetime import datetime, timedelta

class ReportesController:
    def __init__(self, main_view, db_model):
        self.view = main_view
        self.db_model = db_model
        self.reportes_view = ReportesView(main_view)
    
    def mostrar_reportes(self):
        """Muestra el menú de reportes"""
        self.reportes_view.mostrar_menu_reportes(self)
    
    def reporte_ventas_pelicula(self):
        """Genera reporte de ventas por película"""
        try:
            # Obtener rango de fechas (últimos 30 días)
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=30)
            
            query = """
            SELECT p.titulo, COUNT(b.id_boleto) as boletos_vendidos, 
                   SUM(f.precio) as ingresos_totales
            FROM peliculas p
            JOIN funciones f ON p.id_pelicula = f.id_pelicula
            LEFT JOIN boletos b ON f.id_funcion = b.id_funcion
            WHERE f.horario BETWEEN %s AND %s
            GROUP BY p.id_pelicula
            ORDER BY ingresos_totales DESC
            """
            
            resultados = self.db_model.ejecutar_consulta(query, (fecha_inicio, fecha_fin)).fetchall()
            
            # Preparar datos para la vista
            datos = []
            total_boletos = 0
            total_ingresos = 0.0
            
            for resultado in resultados:
                ingresos = resultado['ingresos_totales'] or 0
                datos.append({
                    'Película': resultado['titulo'],
                    'Boletos Vendidos': resultado['boletos_vendidos'] or 0,
                    'Ingresos Totales': f"${ingresos:.2f}"
                })
                total_boletos += resultado['boletos_vendidos'] or 0
                total_ingresos += ingresos
            
            # Agregar totales
            datos.append({
                'Película': 'TOTAL',
                'Boletos Vendidos': total_boletos,
                'Ingresos Totales': f"${total_ingresos:.2f}"
            })
            
            titulo = f"VENTAS POR PELÍCULA ({fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')})"
            columnas = ["Película", "Boletos Vendidos", "Ingresos Totales"]
            
            self.reportes_view.mostrar_reporte(datos, titulo, columnas, self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")