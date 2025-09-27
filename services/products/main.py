from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import db_manager
from shared.models import ProductCreate, ProductResponse
from shared.auth import require_admin, get_current_user
import aiofiles
import uuid
from PIL import Image
import logging
from typing import Optional, List

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineMagic Products Service", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de archivos
UPLOAD_DIR = "uploads/products"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Crear directorio de uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Validar extensión de archivo"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

def generate_unique_filename(original_filename: str) -> str:
    """Generar nombre único para archivo"""
    extension = os.path.splitext(original_filename)[1].lower()
    unique_name = f"{uuid.uuid4()}{extension}"
    return unique_name

async def save_uploaded_file(file: UploadFile) -> str:
    """Guardar archivo subido"""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")
    
    # Generar nombre único
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Guardar archivo
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Retornar URL relativa
    return f"/uploads/products/{unique_filename}"

def optimize_image(file_path: str, max_width: int = 400, quality: int = 85):
    """Optimizar imagen de producto"""
    try:
        with Image.open(file_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar si es necesario
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Guardar optimizada
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        logger.warning(f"No se pudo optimizar imagen {file_path}: {e}")

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    try:
        db_manager.execute_query("SELECT 1")
        return {"status": "healthy", "service": "products"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/", response_model=List[ProductResponse])
async def get_products(
    categoria: Optional[str] = None,
    disponible: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Obtener lista de productos"""
    try:
        base_query = """
        SELECT id_producto, nombre, descripcion, precio, categoria, stock, 
               imagen_url, fecha_creacion
        FROM productos 
        WHERE 1=1
        """
        params = []
        
        if categoria:
            base_query += " AND categoria = %s"
            params.append(categoria)
        
        if disponible:
            base_query += " AND stock > 0"
        
        base_query += " ORDER BY categoria, nombre LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        products = db_manager.execute_query(base_query, tuple(params))
        return products
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Obtener producto por ID"""
    try:
        product = db_manager.execute_query(
            """SELECT id_producto, nombre, descripcion, precio, categoria, stock,
                      imagen_url, fecha_creacion
               FROM productos WHERE id_producto = %s""",
            (product_id,)
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return product[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/", response_model=dict)
async def create_product(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio: float = Form(...),
    categoria: str = Form(...),
    stock: int = Form(...),
    imagen: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_admin)
):
    """Crear nuevo producto (solo admin)"""
    try:
        if precio <= 0:
            raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0")
        
        if stock < 0:
            raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
        
        imagen_url = None
        
        # Procesar imagen si se proporciona
        if imagen:
            if not validate_file_extension(imagen.filename, ALLOWED_IMAGE_EXTENSIONS):
                raise HTTPException(status_code=400, detail="Formato de imagen no válido")
            
            imagen_url = await save_uploaded_file(imagen)
            # Optimizar imagen
            full_path = os.path.join(UPLOAD_DIR, os.path.basename(imagen_url))
            optimize_image(full_path)
        
        # Insertar producto en base de datos
        product_id = db_manager.execute_query(
            """INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen_url)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, descripcion, precio, categoria, stock, imagen_url),
            fetch=False
        )
        
        logger.info(f"Producto creado: {nombre} (ID: {product_id})")
        return {
            "message": "Producto creado exitosamente",
            "product_id": product_id,
            "imagen_url": imagen_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/{product_id}", response_model=dict)
async def update_product(
    product_id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio: Optional[float] = Form(None),
    categoria: Optional[str] = Form(None),
    stock: Optional[int] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_admin)
):
    """Actualizar producto (solo admin)"""
    try:
        # Verificar que el producto existe
        existing_product = db_manager.execute_query(
            "SELECT * FROM productos WHERE id_producto = %s",
            (product_id,)
        )
        
        if not existing_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        product = existing_product[0]
        
        # Preparar datos para actualizar
        update_data = {}
        if nombre is not None:
            update_data['nombre'] = nombre
        if descripcion is not None:
            update_data['descripcion'] = descripcion
        if precio is not None:
            if precio <= 0:
                raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0")
            update_data['precio'] = precio
        if categoria is not None:
            update_data['categoria'] = categoria
        if stock is not None:
            if stock < 0:
                raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
            update_data['stock'] = stock
        
        # Procesar nueva imagen
        if imagen:
            if not validate_file_extension(imagen.filename, ALLOWED_IMAGE_EXTENSIONS):
                raise HTTPException(status_code=400, detail="Formato de imagen no válido")
            
            # Eliminar imagen anterior si existe
            if product['imagen_url']:
                old_image_path = os.path.join(".", product['imagen_url'].lstrip('/'))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            imagen_url = await save_uploaded_file(imagen)
            full_path = os.path.join(UPLOAD_DIR, os.path.basename(imagen_url))
            optimize_image(full_path)
            update_data['imagen_url'] = imagen_url
        
        # Actualizar base de datos si hay cambios
        if update_data:
            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values()) + [product_id]
            
            db_manager.execute_query(
                f"UPDATE productos SET {set_clause} WHERE id_producto = %s",
                tuple(values),
                fetch=False
            )
        
        logger.info(f"Producto actualizado: {product_id}")
        return {"message": "Producto actualizado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/{product_id}")
async def delete_product(product_id: int, current_user: dict = Depends(require_admin)):
    """Eliminar producto (solo admin)"""
    try:
        # Obtener información del producto
        product = db_manager.execute_query(
            "SELECT imagen_url FROM productos WHERE id_producto = %s",
            (product_id,)
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Eliminar archivo de imagen si existe
        product_data = product[0]
        if product_data['imagen_url']:
            image_path = os.path.join(".", product_data['imagen_url'].lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Eliminar de base de datos
        affected_rows = db_manager.execute_query(
            "DELETE FROM productos WHERE id_producto = %s",
            (product_id,),
            fetch=False
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        logger.info(f"Producto eliminado: {product_id}")
        return {"message": "Producto eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/categories/list")
async def get_categories():
    """Obtener lista de categorías disponibles"""
    try:
        categories = db_manager.execute_query(
            """SELECT categoria, COUNT(*) as cantidad, AVG(precio) as precio_promedio
               FROM productos 
               WHERE stock > 0
               GROUP BY categoria
               ORDER BY categoria"""
        )
        
        return categories
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/combos/popular")
async def get_popular_combos():
    """Obtener combos más populares"""
    try:
        combos = db_manager.execute_query(
            """SELECT p.*, COALESCE(v.total_vendido, 0) as total_vendido
               FROM productos p
               LEFT JOIN (
                   SELECT id_producto, SUM(cantidad) as total_vendido
                   FROM ventas_productos
                   WHERE fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                   GROUP BY id_producto
               ) v ON p.id_producto = v.id_producto
               WHERE p.categoria = 'combo' AND p.stock > 0
               ORDER BY total_vendido DESC, p.precio ASC
               LIMIT 6"""
        )
        
        return combos
    except Exception as e:
        logger.error(f"Error obteniendo combos populares: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/{product_id}/stock")
async def update_stock(
    product_id: int, 
    cantidad: int,
    operacion: str,  # 'add' o 'subtract'
    current_user: dict = Depends(require_admin)
):
    """Actualizar stock de producto (solo admin)"""
    try:
        if operacion not in ['add', 'subtract']:
            raise HTTPException(status_code=400, detail="Operación debe ser 'add' o 'subtract'")
        
        # Obtener stock actual
        product = db_manager.execute_query(
            "SELECT stock FROM productos WHERE id_producto = %s",
            (product_id,)
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        current_stock = product[0]['stock']
        
        if operacion == 'add':
            new_stock = current_stock + cantidad
        else:  # subtract
            new_stock = current_stock - cantidad
            if new_stock < 0:
                raise HTTPException(status_code=400, detail="Stock insuficiente")
        
        # Actualizar stock
        db_manager.execute_query(
            "UPDATE productos SET stock = %s WHERE id_producto = %s",
            (new_stock, product_id),
            fetch=False
        )
        
        logger.info(f"Stock actualizado para producto {product_id}: {current_stock} -> {new_stock}")
        return {
            "message": "Stock actualizado exitosamente",
            "stock_anterior": current_stock,
            "stock_nuevo": new_stock
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando stock: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/sales/stats")
async def get_sales_stats(current_user: dict = Depends(require_admin)):
    """Obtener estadísticas de ventas (solo admin)"""
    try:
        # Ventas por categoría
        category_stats = db_manager.execute_query(
            """SELECT p.categoria, 
                      COUNT(v.id_venta) as total_ventas,
                      SUM(v.cantidad) as total_cantidad,
                      SUM(v.total) as total_ingresos
               FROM ventas_productos v
               JOIN productos p ON v.id_producto = p.id_producto
               WHERE v.fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)
               GROUP BY p.categoria
               ORDER BY total_ingresos DESC"""
        )
        
        # Productos más vendidos
        top_products = db_manager.execute_query(
            """SELECT p.nombre, p.categoria, 
                      SUM(v.cantidad) as total_vendido,
                      SUM(v.total) as ingresos
               FROM ventas_productos v
               JOIN productos p ON v.id_producto = p.id_producto
               WHERE v.fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)
               GROUP BY v.id_producto
               ORDER BY total_vendido DESC
               LIMIT 10"""
        )
        
        # Ingresos totales
        total_revenue = db_manager.execute_query(
            """SELECT SUM(total) as ingresos_totales,
                      COUNT(DISTINCT id_usuario) as clientes_unicos
               FROM ventas_productos
               WHERE fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)"""
        )
        
        return {
            "categoria_stats": category_stats,
            "productos_top": top_products,
            "resumen": total_revenue[0] if total_revenue else {"ingresos_totales": 0, "clientes_unicos": 0}
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
