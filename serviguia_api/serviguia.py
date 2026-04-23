"""
serviguia.py
Lógica central del módulo ServiGuía.

Contiene:
  - mock_llm():            Simula las respuestas del LLM para los 8 casos de prueba.
  - llamar_llm_real():     Llama a GPT-5 vía API de OpenAI.
  - filtrar_trabajadores(): Filtra por categoría y disponibilidad.
  - rankear_trabajadores(): Ordena por calificación e insignias.
  - procesar_diagnostico(): Función principal que orquesta todo.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Cargar variables de entorno desde .env (funciona independiente del terminal de VS Code)
load_dotenv()

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────
# Carga de la base de datos de trabajadores
# ────────────────────────────────────────────────
RUTA_TRABAJADORES = Path(__file__).parent / "data" / "trabajadores.json"

def cargar_trabajadores() -> list[dict]:
    """Carga el archivo JSON de trabajadores."""
    with open(RUTA_TRABAJADORES, "r", encoding="utf-8") as f:
        return json.load(f)


# ────────────────────────────────────────────────
# MOCK DEL LLM  (reemplazar con llamar_llm_real)
# ────────────────────────────────────────────────

# Tabla de detección de palabras clave para cada caso de prueba
PALABRAS_CLAVE = {
    "CRITICO_GAS":       ["gas", "olor a gas", "huele a gas", "fuga de gas"],
    "CRITICO_CHISPAS":   ["chispa", "chispas", "cable quemado", "contacto quemado", "corto electrico"],
    "CRITICO_INCENDIO":  ["humo", "incendio", "fuego", "se está quemando"],
    "CRITICO_INUNDACION":["inundación", "inundacion", "agua por todos lados", "se inundó"],
    "GOTERA":            ["gotera", "goteras", "llueve adentro", "cuando llueve"],
    "AC":                ["aire acondicionado", "ac", "minisplit", "no enfría", "no enfria"],
    "LUZ_PARCIAL":       ["se fue la luz", "sin luz en", "cuartos sin luz", "luz en dos", "luz en un"],
    "BANO_AMBIGUO":      ["baño", "bano", "inodoro", "excusado", "regadera", "lavabo"],
    "REFRIGERADOR":      ["refrigerador", "refri", "no enfría bien", "no enfria bien"],
    "FUGA_FREGADERO":    ["agua saliendo", "fregadero", "fuga en el fregadero", "agua por el fregadero"],
}


def _texto_contiene(texto: str, palabras: list[str]) -> bool:
    """Verifica si el texto contiene alguna de las palabras clave (case insensitive)."""
    texto_lower = texto.lower()
    return any(p in texto_lower for p in palabras)


def mock_llm(descripcion_usuario: str) -> dict:
    """
    Simula la respuesta del LLM (GPT-4o) para los 8 casos de prueba.

    Cuando tengamos la API key de OpenAI, esta función se REEMPLAZA
    por llamar_llm_real() sin cambiar nada más.

    Retorna el schema JSON definido en el documento ServiGuía.
    """

    # ── C-01: Olor a gas (CRÍTICO) ──────────────────────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["CRITICO_GAS"]):
        return {
            "nivel_urgencia": "CRÍTICO",
            "es_emergencia": True,
            "accion_inmediata": (
                "1. Sal de la casa inmediatamente sin encender ningún aparato. "
                "2. No toques apagadores ni interruptores. "
                "3. Desde afuera llama al 911."
            ),
            "categoria_detectada": None,
            "pregunta_seguimiento": None,
            "resumen_diagnostico": "Posible fuga de gas detectada. Es una emergencia de riesgo de vida.",
            "proveedores_sugeridos": [],
            "numero_emergencia": "911",
        }

    # ── C-02: Chispas o cable quemado (CRÍTICO) ─────────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["CRITICO_CHISPAS"]):
        return {
            "nivel_urgencia": "CRÍTICO",
            "es_emergencia": True,
            "accion_inmediata": (
                "1. Baja el interruptor general de la casa si puedes hacerlo sin riesgo. "
                "2. No toques el cable. "
                "3. Llama al 911 de inmediato."
            ),
            "categoria_detectada": None,
            "pregunta_seguimiento": None,
            "resumen_diagnostico": "Chispas o cable quemado detectado. Es una emergencia eléctrica de riesgo de vida.",
            "proveedores_sugeridos": [],
            "numero_emergencia": "911",
        }

    # ── C-03: Incendio / humo (CRÍTICO) ─────────────────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["CRITICO_INCENDIO"]):
        return {
            "nivel_urgencia": "CRÍTICO",
            "es_emergencia": True,
            "accion_inmediata": (
                "1. Sal de la casa de inmediato por la salida más cercana. "
                "2. No busques objetos. "
                "3. Llama al 911."
            ),
            "categoria_detectada": None,
            "pregunta_seguimiento": None,
            "resumen_diagnostico": "Posible incendio o presencia de humo. Evacúa inmediatamente.",
            "proveedores_sugeridos": [],
            "numero_emergencia": "911",
        }

    # ── Inundación severa (CRÍTICO) ──────────────────────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["CRITICO_INUNDACION"]):
        return {
            "nivel_urgencia": "CRÍTICO",
            "es_emergencia": True,
            "accion_inmediata": (
                "1. Cierra la llave de paso general del agua. "
                "2. Cierra la llave del tinaco si tienes acceso. "
                "3. Si hay riesgo, sal de la casa y llama al 911."
            ),
            "categoria_detectada": None,
            "pregunta_seguimiento": None,
            "resumen_diagnostico": "Inundación severa detectada. Corta el suministro de agua y evacúa si hay riesgo.",
            "proveedores_sugeridos": [],
            "numero_emergencia": "911",
        }

    # ── C-08: Agua saliendo por fregadero (MODERADO) ─────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["FUGA_FREGADERO"]):
        return {
            "nivel_urgencia": "MODERADO",
            "es_emergencia": False,
            "accion_inmediata": (
                "Cierra la llave de paso del fregadero o la llave general "
                "para evitar que se acumule más agua."
            ),
            "categoria_detectada": "plomeria.fugas_menores",
            "pregunta_seguimiento": None,
            "resumen_diagnostico": (
                "Hay una fuga activa en el fregadero. "
                "Cierra el agua y contacta a un plomero pronto."
            ),
            "proveedores_sugeridos": ["t001", "t002"],
            "numero_emergencia": None,
        }

    # ── C-03: Gotera en el techo (NORMAL) ────────────────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["GOTERA"]):
        return {
            "nivel_urgencia": "NORMAL",
            "es_emergencia": False,
            "accion_inmediata": None,
            "categoria_detectada": "construccion.impermeabilizacion",
            "pregunta_seguimiento": None,
            "resumen_diagnostico": (
                "Tienes una gotera en el techo que aparece cuando llueve. "
                "Se necesita impermeabilización."
            ),
            "proveedores_sugeridos": ["t007"],
            "numero_emergencia": None,
        }

    # ── C-07: Refrigerador no enfría (NORMAL) ─────────────────────────────────
    # IMPORTANTE: va ANTES que AC porque "no enfría bien" puede confundirse
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["REFRIGERADOR"]):
        return {
            "nivel_urgencia": "NORMAL",
            "es_emergencia": False,
            "accion_inmediata": None,
            "categoria_detectada": "reparaciones.refrigeradores",
            "pregunta_seguimiento": None,
            "resumen_diagnostico": (
                "Tu refrigerador no está enfriando bien. "
                "Puede ser el termostato, el compresor o el gas refrigerante."
            ),
            "proveedores_sugeridos": ["t010"],
            "numero_emergencia": None,
        }

    # ── C-04: Aire acondicionado no enfría (NORMAL) ───────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["AC"]):
        return {
            "nivel_urgencia": "NORMAL",
            "es_emergencia": False,
            "accion_inmediata": None,
            "categoria_detectada": "clima.reparacion_ac",
            "pregunta_seguimiento": None,
            "resumen_diagnostico": (
                "Tu aire acondicionado no está enfriando correctamente. "
                "Puede ser falta de gas refrigerante o un problema mecánico."
            ),
            "proveedores_sugeridos": ["t005", "t006"],
            "numero_emergencia": None,
        }

    # ── C-05: Se fue la luz en dos cuartos (NORMAL) ───────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["LUZ_PARCIAL"]):
        return {
            "nivel_urgencia": "NORMAL",
            "es_emergencia": False,
            "accion_inmediata": None,
            "categoria_detectada": "electricidad",
            "pregunta_seguimiento": None,
            "resumen_diagnostico": (
                "La luz se fue solo en algunos cuartos. "
                "Probablemente un circuito del tablero se disparó."
            ),
            "proveedores_sugeridos": ["t003"],
            "numero_emergencia": None,
        }

    # ── C-06: Algo se descompuso en el baño (AMBIGUO) ─────────────────────────
    if _texto_contiene(descripcion_usuario, PALABRAS_CLAVE["BANO_AMBIGUO"]):
        return {
            "nivel_urgencia": "NORMAL",
            "es_emergencia": False,
            "accion_inmediata": None,
            "categoria_detectada": None,
            "pregunta_seguimiento": (
                "¿Qué parte del baño tiene el problema? "
                "¿La regadera, el excusado, el lavabo o la tubería?"
            ),
            "resumen_diagnostico": (
                "Hay un problema en el baño pero necesito más detalles "
                "para recomendarte al profesional correcto."
            ),
            "proveedores_sugeridos": [],
            "numero_emergencia": None,
        }

    # ── Caso genérico / no reconocido ────────────────────────────────────────
    return {
        "nivel_urgencia": "NORMAL",
        "es_emergencia": False,
        "accion_inmediata": None,
        "categoria_detectada": None,
        "pregunta_seguimiento": (
            "¿Puedes darme más detalles sobre el problema? "
            "Por ejemplo, ¿en qué parte de la casa ocurre y desde cuándo?"
        ),
        "resumen_diagnostico": "No pude identificar el problema. Por favor dime más detalles.",
        "proveedores_sugeridos": [],
        "numero_emergencia": None,
    }


# ────────────────────────────────────────────────
# LLM REAL  (GPT-4o via OpenAI API)
# ────────────────────────────────────────────────

def llamar_llm_real(descripcion_usuario: str, imagen_base64: Optional[str] = None) -> dict:
    """
    Llama a GPT-4o usando la API de OpenAI.

    Requiere OPENAI_API_KEY en el archivo .env.
    Si ocurre un error (cuota, key inválida, red), hace fallback a mock_llm()
    y registra el error en el log.
    """
    from openai import OpenAI, OpenAIError

    api_key = os.environ.get("OPENAI_API_KEY", "")
    modelo  = os.environ.get("OPENAI_MODEL", "gpt-5-nano")

    if not api_key or api_key.startswith("sk-XXXX"):
        logger.warning("OPENAI_API_KEY no configurada. Usando mock_llm como fallback.")
        return mock_llm(descripcion_usuario)

    cliente = OpenAI(api_key=api_key)

    system_prompt = """Eres ServiGuia, el asistente de diagnóstico de una app de servicios
del hogar llamada ServiApp, en Hermosillo, Sonora, Mexico.

Tu trabajo es:
1. Detectar si la situación es una EMERGENCIA de riesgo de vida.
2. Si no es emergencia, clasificar el problema en una categoría.
3. Hacer máximo 2 preguntas si necesitas más información.
4. Devolver SIEMPRE una respuesta en formato JSON estructurado.

NIVELES DE URGENCIA:
- CRÍTICO: riesgo de vida (gas, incendio, electrocución, inundación)
- MODERADO: daño activo que puede empeorar (fuga activa, corto)
- NORMAL: problema sin urgencia inmediata

CATEGORÍAS VÁLIDAS (usa exactamente estos IDs):
electricidad | plomeria | plomeria.fugas_menores | plomeria.tinacos |
plomeria.lavadora_secadora | plomeria.hidroneumaticos | reparaciones |
reparaciones.lavadoras | reparaciones.secadoras | reparaciones.refrigeradores |
reparaciones.estufas | reparaciones.calentones | reparaciones.hornos_microondas |
carpinteria | construccion | construccion.albanileria |
construccion.impermeabilizacion | construccion.tablaroca |
fumigacion | clima | clima.instalacion_ac | clima.ducteros |
clima.reparacion_abanicos | clima.reparacion_ac | pintura |
limpieza | limpieza.alfombras | limpieza.colchones | limpieza.salas |
seguridad | seguridad.alarmas | computo | computo.soporte

CASOS CRÍTICOS (no sugieras proveedores, proveedores_sugeridos debe ser []):
- Olor a gas: salir, no encender luz, llamar al 911
- Incendio o humo: salir, llamar al 911
- Cables con chispas: cortar luz general, llamar al 911

Responde SIEMPRE en español simple para adultos mayores.
Devuelve SOLO el JSON con este schema exacto, sin texto adicional:
{
  "nivel_urgencia": "CRÍTICO | MODERADO | NORMAL",
  "es_emergencia": true | false,
  "accion_inmediata": "Texto o null",
  "categoria_detectada": "ID de categoria o null",
  "pregunta_seguimiento": "Pregunta o null",
  "resumen_diagnostico": "1-2 oraciones",
  "proveedores_sugeridos": [],
  "numero_emergencia": "911 | null"
}"""

    # Construye el mensaje (texto, o texto + imagen si se envió foto)
    contenido_usuario: list = [{"type": "text", "text": descripcion_usuario}]
    if imagen_base64:
        contenido_usuario.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"},
        })

    try:
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contenido_usuario},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        resultado = json.loads(respuesta.choices[0].message.content)

        # Validar que el JSON tenga los campos mínimos requeridos
        campos_requeridos = [
            "nivel_urgencia", "es_emergencia", "resumen_diagnostico", "proveedores_sugeridos"
        ]
        for campo in campos_requeridos:
            if campo not in resultado:
                raise ValueError(f"GPT-4o no devolvió el campo requerido: '{campo}'")

        # Asegurar que proveedores_sugeridos siempre sea lista
        if not isinstance(resultado.get("proveedores_sugeridos"), list):
            resultado["proveedores_sugeridos"] = []

        logger.info("GPT-4o respondió correctamente. Urgencia: %s", resultado.get("nivel_urgencia"))
        return resultado

    except OpenAIError as e:
        logger.error("Error de OpenAI API: %s. Usando mock_llm como fallback.", e)
        return mock_llm(descripcion_usuario)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Error al parsear respuesta de GPT-4o: %s. Usando mock_llm como fallback.", e)
        return mock_llm(descripcion_usuario)


# ────────────────────────────────────────────────
# FILTRADO Y RANKING
# ────────────────────────────────────────────────

# Valor numérico de cada insignia para el ranking
PESO_INSIGNIA = {
    "experiencia_top": 3,
    "certificado": 2,
    "siempre_puntual": 2,
    "trabajador_formal": 1,
}


def filtrar_trabajadores(trabajadores: list[dict], categoria: str) -> list[dict]:
    """
    Filtra trabajadores por categoría detectada y disponibilidad.

    Un trabajador aplica si:
    - está disponible (disponible == True)
    - tiene la categoría exacta O la categoría padre en su lista
      Ejemplo: categoria "plomeria.fugas_menores"
               → acepta trabajadores con "plomeria" o "plomeria.fugas_menores"
    """
    if not categoria:
        return []

    # Categoría padre: "plomeria.fugas_menores" → "plomeria"
    categoria_padre = categoria.split(".")[0]

    resultado = []
    for trabajador in trabajadores:
        if not trabajador.get("disponible", False):
            continue  # salta trabajadores no disponibles
        categorias_trabajador = trabajador.get("categorias", [])
        if categoria in categorias_trabajador or categoria_padre in categorias_trabajador:
            resultado.append(trabajador)

    return resultado


def rankear_trabajadores(trabajadores: list[dict]) -> list[dict]:
    """
    Ordena trabajadores por:
    1. Calificación global (mayor es mejor)
    2. Suma de pesos de insignias (desempate)
    3. Total de reviews (desempate final)

    Retorna lista ordenada de mejor a peor.
    """
    def puntaje(t: dict) -> tuple:
        suma_insignias = sum(
            PESO_INSIGNIA.get(ins, 0) for ins in t.get("insignias", [])
        )
        return (
            t.get("calificacion_global", 0),  # primario: calificación
            suma_insignias,                    # secundario: insignias
            t.get("total_reviews", 0),         # terciario: reviews
        )

    return sorted(trabajadores, key=puntaje, reverse=True)


# ────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ────────────────────────────────────────────────

def procesar_diagnostico(descripcion_usuario: str, imagen_base64: Optional[str] = None) -> dict:
    """
    Orquesta el flujo completo de ServiGuía:
      1. Llama al LLM (GPT-4o real en producción, mock en desarrollo)
      2. Si hay categoría detectada, filtra y rankea trabajadores
      3. Reemplaza la lista de proveedores con los IDs rankeados

    La selección del LLM se controla con la variable de entorno ENTORNO:
      - ENTORNO=production  → llama a GPT-4o (llamar_llm_real)
      - ENTORNO=development → usa el mock basado en palabras clave (mock_llm)

    Returns:
        dict con el schema JSON completo listo para devolver al cliente.
    """
    # Paso 1: Seleccionar LLM según entorno
    entorno = os.environ.get("ENTORNO", "development").lower()
    if entorno == "production":
        logger.info("Modo PRODUCTION → llamando a GPT-4o real")
        respuesta = llamar_llm_real(descripcion_usuario, imagen_base64)
    else:
        logger.info("Modo DEVELOPMENT → usando mock_llm")
        respuesta = mock_llm(descripcion_usuario)

    # Paso 2: Si es emergencia, retornar sin buscar proveedores
    if respuesta.get("es_emergencia"):
        return respuesta

    # Paso 3: Si hay categoría, filtrar y rankear proveedores
    categoria = respuesta.get("categoria_detectada")
    if categoria:
        todos_los_trabajadores = cargar_trabajadores()
        filtrados = filtrar_trabajadores(todos_los_trabajadores, categoria)
        rankeados = rankear_trabajadores(filtrados)
        # Solo devolvemos los IDs (máximo 3 sugeridos)
        respuesta["proveedores_sugeridos"] = [t["id"] for t in rankeados[:3]]

    return respuesta
