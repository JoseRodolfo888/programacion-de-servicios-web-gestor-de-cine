from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import os
from typing import Optional
import asyncio

app = FastAPI(title="CineMagic Gateway", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de servicios (cambio con los nombres de los contenedores)
SERVICES = {
    "auth": "http://auth_service:8001",
    "movies": "http://movies_service:8002", 
    "theaters": "http://theaters_service:8003",
    "products": "http://products_service:8004",
    "tickets": "http://tickets_service:8005"
}

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Servir la página principal"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Verificar estado de todos los servicios"""
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "url": service_url
                }
    
    return {"gateway": "healthy", "services": health_status}

async def forward_request(service: str, path: str, method: str, request: Request):
    """Reenviar peticiones a los microservicios"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_url = SERVICES[service]
    url = f"{service_url}{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            # Si el microservicio devolvió un error lo reenviamos al cliente
            if response.status_code >= 400:
                try:
                    detail = response.json()
                except Exception:
                    detail = {"detail": response.text or "Error desconocido del servicio"}
                raise HTTPException(status_code=response.status_code, detail=detail)

            # Si la respuesta no tiene contenido, devolvemos la respuesta vacía
            if response.status_code == 204:
                return Response(status_code=204)

            # Si todo está bien, devolvemos el contenido
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# Rutas del servicio de autenticación
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    return await forward_request("auth", f"/{path}", request.method, request)

# Rutas del servicio de películas
@app.api_route("/api/movies/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def movies_proxy(path: str, request: Request):
    return await forward_request("movies", f"/{path}", request.method, request)

# Rutas del servicio de salas y funciones
@app.api_route("/api/theaters/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def theaters_proxy(path: str, request: Request):
    return await forward_request("theaters", f"/{path}", request.method, request)

# Rutas del servicio de productos
@app.api_route("/api/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def products_proxy(path: str, request: Request):
    return await forward_request("products", f"/{path}", request.method, request)

# Rutas del servicio de boletos
@app.api_route("/api/tickets/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def tickets_proxy(path: str, request: Request):
    return await forward_request("tickets", f"/{path}", request.method, request)

if __name__ == "__main__":
    import uvicorn
    # Crear directorios necesarios
    os.makedirs("static", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("uploads/movies", exist_ok=True)
    os.makedirs("uploads/products", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
