"""
Punto de entrada de la API del concesionario.

Ejecutar en desarrollo:
    uvicorn app.main:app --reload

Documentación interactiva (generada automáticamente por FastAPI a
partir de los esquemas Pydantic y los routers):
    http://127.0.0.1:8000/docs
"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, cars, orders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("concesionario_api")

app = FastAPI(
    title="API Concesionario de Coches",
    description=(
        "API de ejemplo para gestionar un catálogo de coches y sus "
        "pedidos, con autenticación JWT. Laboratorio del módulo "
        "'APIs web con FastAPI'."
    ),
    version="1.0.0",
)

# --- CORS: quién puede llamar a la API desde el navegador ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción: lista de dominios concretos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Middleware personalizado: mide el tiempo de cada petición ---
@app.middleware("http")
async def agregar_tiempo_proceso(request: Request, call_next):
    inicio = time.time()
    response = await call_next(request)
    duracion = time.time() - inicio
    response.headers["X-Process-Time"] = f"{duracion:.4f}"
    logger.info(
        "%s %s -> %s (%.4fs)",
        request.method,
        request.url.path,
        response.status_code,
        duracion,
    )
    return response


# Crea las tablas si no existen. En un proyecto real se usarían
# migraciones (p. ej. Alembic) en lugar de create_all.
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(orders.router)


@app.get("/", tags=["Salud"])
def raiz():
    return {"mensaje": "API Concesionario de Coches activa", "docs": "/docs"}
