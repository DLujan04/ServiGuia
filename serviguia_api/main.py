"""
main.py
Servidor FastAPI para el módulo ServiGuía.

Endpoint principal:
  POST /api/diagnostico  →  recibe descripción del usuario y devuelve JSON diagnóstico.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
import uvicorn

from serviguia import procesar_diagnostico, cargar_trabajadores

# Directorio de archivos estáticos (chat.html)
RUTA_STATIC = Path(__file__).parent / "static"

# ────────────────────────────────────────────────
# Configuración de la aplicación
# ────────────────────────────────────────────────
app = FastAPI(
    title="ServiGuía API",
    description="Módulo de diagnóstico inteligente con IA para ServiApp – Hermosillo, Sonora.",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI en /docs
    redoc_url="/redoc",     # ReDoc en /redoc
)

# CORS: permite que el frontend de ServiApp consuma esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (chat.html y futuros assets)
app.mount("/static", StaticFiles(directory=RUTA_STATIC), name="static")


# ────────────────────────────────────────────────
# Modelos de entrada y salida (Pydantic)
# ────────────────────────────────────────────────

class SolicitudDiagnostico(BaseModel):
    """Cuerpo del request que manda el usuario."""
    descripcion: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Descripción del problema en palabras del usuario.",
        examples=["Mi casa huele mucho a gas"],
    )
    imagen_base64: Optional[str] = Field(
        default=None,
        description="Foto del problema codificada en base64 (opcional, para GPT-4o Vision).",
    )

class RespuestaDiagnostico(BaseModel):
    """Schema de respuesta exacto definido en el documento ServiGuía."""
    nivel_urgencia: str
    es_emergencia: bool
    accion_inmediata: Optional[str]
    categoria_detectada: Optional[str]
    pregunta_seguimiento: Optional[str]
    resumen_diagnostico: str
    proveedores_sugeridos: list[str]
    numero_emergencia: Optional[str]

class RespuestaTrabajador(BaseModel):
    """Datos públicos de un proveedor de servicio."""
    id: str
    nombre: str
    categorias: list[str]
    calificacion_global: float
    insignias: list[str]
    disponible: bool
    precio_desde: int
    precio_hasta: int
    total_reviews: int


# ────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────

@app.get("/", tags=["Estado"])
def raiz():
    """Redirige a la interfaz de chat."""
    return RedirectResponse(url="/chat")


@app.get("/chat", tags=["Interfaz"], include_in_schema=False)
def interfaz_chat():
    """Sirve la interfaz de chat web para pruebas manuales."""
    return FileResponse(RUTA_STATIC / "chat.html")


@app.get("/health", tags=["Estado"])
def health_check():
    """Health check para monitoreo."""
    return {"status": "ok"}


@app.get(
    "/api/trabajador/{trabajador_id}",
    response_model=RespuestaTrabajador,
    summary="Consultar datos de un proveedor",
    description="Devuelve los datos públicos de un proveedor dado su ID (ej. t001).",
    tags=["Proveedores"],
)
def obtener_trabajador(trabajador_id: str) -> RespuestaTrabajador:
    """Busca un trabajador por ID en la base de datos local."""
    trabajadores = cargar_trabajadores()
    for t in trabajadores:
        if t["id"] == trabajador_id:
            return RespuestaTrabajador(**t)
    raise HTTPException(status_code=404, detail=f"Proveedor '{trabajador_id}' no encontrado.")


@app.post(
    "/api/diagnostico",
    response_model=RespuestaDiagnostico,
    summary="Diagnosticar problema del hogar",
    description=(
        "Recibe la descripción de un problema en el hogar (y opcionalmente una imagen) "
        "y devuelve un diagnóstico estructurado con nivel de urgencia, categoría, "
        "acciones a seguir y proveedores sugeridos."
    ),
    tags=["Diagnóstico"],
)
def diagnostico(solicitud: SolicitudDiagnostico) -> RespuestaDiagnostico:
    """
    Endpoint principal de ServiGuía.

    - **descripcion**: texto libre del usuario describiendo el problema.
    - **imagen_base64**: foto del problema en base64 (opcional).
    """
    try:
        resultado = procesar_diagnostico(
            descripcion_usuario=solicitud.descripcion,
            imagen_base64=solicitud.imagen_base64,
        )
        return RespuestaDiagnostico(**resultado)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar el diagnóstico: {str(e)}",
        )


# ────────────────────────────────────────────────
# Punto de entrada para desarrollo
# ────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
