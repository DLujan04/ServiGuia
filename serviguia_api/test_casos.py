# -*- coding: utf-8 -*-
"""
test_casos.py
Suite de pruebas automáticas para los 8 casos definidos en el documento ServiGuía.

Uso:
    python test_casos.py

Reporta cuántos casos pasan de 8 y detalla los que fallan.
"""

import sys
import json
from serviguia import procesar_diagnostico

# ────────────────────────────────────────────────
# Definición de los 8 casos de prueba del documento
# ────────────────────────────────────────────────
CASOS_DE_PRUEBA = [
    {
        "id": "C-01",
        "descripcion": "Mi casa huele mucho a gas",
        "verificaciones": [
            ("nivel_urgencia", "==", "CRÍTICO"),
            ("es_emergencia", "==", True),
            ("proveedores_sugeridos", "==", []),
            ("numero_emergencia", "==", "911"),
        ],
        "descripcion_esperada": "CRÍTICO, sin proveedores, número 911.",
    },
    {
        "id": "C-02",
        "descripcion": "Hay chispas en el contacto de la cocina",
        "verificaciones": [
            ("nivel_urgencia", "==", "CRÍTICO"),
            ("es_emergencia", "==", True),
            ("proveedores_sugeridos", "==", []),
            ("numero_emergencia", "==", "911"),
        ],
        "descripcion_esperada": "CRÍTICO, sin proveedores, número 911.",
    },
    {
        "id": "C-03",
        "descripcion": "Tengo una gotera en el techo cuando llueve",
        "verificaciones": [
            ("nivel_urgencia", "==", "NORMAL"),
            ("es_emergencia", "==", False),
            ("categoria_detectada", "==", "construccion.impermeabilizacion"),
            ("proveedores_sugeridos", "contiene", "t007"),
        ],
        "descripcion_esperada": "NORMAL, categoría construccion.impermeabilizacion, proveedor t007.",
    },
    {
        "id": "C-04",
        "descripcion": "El aire acondicionado ya no enfría",
        "verificaciones": [
            ("nivel_urgencia", "==", "NORMAL"),
            ("es_emergencia", "==", False),
            ("categoria_detectada", "==", "clima.reparacion_ac"),
            ("proveedores_sugeridos", "contiene", "t005"),
            ("proveedores_sugeridos", "contiene", "t006"),
        ],
        "descripcion_esperada": "NORMAL, categoría clima.reparacion_ac, proveedores t005 y t006.",
    },
    {
        "id": "C-05",
        "descripcion": "Se me fue la luz en dos cuartos nada más",
        "verificaciones": [
            ("nivel_urgencia", "==", "NORMAL"),
            ("es_emergencia", "==", False),
            ("categoria_detectada", "==", "electricidad"),
            ("proveedores_sugeridos", "contiene", "t003"),
        ],
        "descripcion_esperada": "NORMAL, categoría electricidad, proveedor t003.",
    },
    {
        "id": "C-06",
        "descripcion": "Algo se descompuso en el baño",
        "verificaciones": [
            ("nivel_urgencia", "==", "NORMAL"),
            ("es_emergencia", "==", False),
            ("pregunta_seguimiento", "no_es_null", None),
        ],
        "descripcion_esperada": "NORMAL, pregunta de seguimiento (ambiguo).",
    },
    {
        "id": "C-07",
        "descripcion": "Mi refrigerador ya no enfría bien",
        "verificaciones": [
            ("nivel_urgencia", "==", "NORMAL"),
            ("es_emergencia", "==", False),
            ("categoria_detectada", "==", "reparaciones.refrigeradores"),
            ("proveedores_sugeridos", "contiene", "t010"),
        ],
        "descripcion_esperada": "NORMAL, categoría reparaciones.refrigeradores, proveedor t010.",
    },
    {
        "id": "C-08",
        "descripcion": "Hay agua saliendo por el fregadero",
        "verificaciones": [
            ("nivel_urgencia", "==", "MODERADO"),
            ("es_emergencia", "==", False),
            ("accion_inmediata", "no_es_null", None),
            ("proveedores_sugeridos", "contiene", "t001"),
            ("proveedores_sugeridos", "contiene", "t002"),
        ],
        "descripcion_esperada": "MODERADO, acción inmediata, proveedores t001 y t002.",
    },
]


# ────────────────────────────────────────────────
# Motor de evaluación
# ────────────────────────────────────────────────

def verificar_campo(campo: str, operador: str, esperado, resultado: dict) -> tuple[bool, str]:
    """
    Evalúa una condición sobre el resultado.

    Operadores disponibles:
      "=="         → valor exacto
      "contiene"   → el campo es una lista y contiene el valor
      "no_es_null" → el campo no es None ni lista vacía
    """
    valor_real = resultado.get(campo)

    if operador == "==":
        ok = valor_real == esperado
        mensaje = f"  [{campo}] esperado={esperado!r}, obtenido={valor_real!r}"
    elif operador == "contiene":
        ok = isinstance(valor_real, list) and esperado in valor_real
        mensaje = f"  [{campo}] debe contener {esperado!r}, obtenido={valor_real!r}"
    elif operador == "no_es_null":
        ok = valor_real is not None and valor_real != [] and valor_real != ""
        mensaje = f"  [{campo}] debe ser no nulo/vacío, obtenido={valor_real!r}"
    else:
        ok = False
        mensaje = f"  Operador desconocido: {operador}"

    return ok, mensaje


def ejecutar_prueba(caso: dict) -> tuple[bool, list[str]]:
    """Ejecuta un caso de prueba y retorna (pasó, lista de errores)."""
    resultado = procesar_diagnostico(caso["descripcion"])
    errores = []

    for campo, operador, esperado in caso["verificaciones"]:
        ok, mensaje = verificar_campo(campo, operador, esperado, resultado)
        if not ok:
            errores.append(mensaje)

    return len(errores) == 0, errores


# ────────────────────────────────────────────────
# Runner principal
# ────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SUITE DE PRUEBAS – ServiGuía")
    print("=" * 60)

    total   = len(CASOS_DE_PRUEBA)
    pasados = 0
    fallidos = []

    for caso in CASOS_DE_PRUEBA:
        paso, errores = ejecutar_prueba(caso)

        if paso:
            pasados += 1
            estado = "[PASO]"
        else:
            fallidos.append((caso["id"], caso["descripcion_esperada"], errores))
            estado = "[FALLO]"

        print(f"\n{estado}  {caso['id']}: \"{caso['descripcion']}\"")
        if errores:
            print(f"  Esperado: {caso['descripcion_esperada']}")
            for err in errores:
                print(err)

    # ── Resumen final ──
    print("\n" + "=" * 60)
    print(f"  RESULTADO: {pasados} de {total} casos pasaron")
    print("=" * 60)

    if pasados == total:
        print("  *** TODOS LOS CASOS PASAN. El mock esta correctamente configurado. ***")
    else:
        print(f"  ATENCION: {total - pasados} caso(s) fallan. Revisa el detalle arriba.")

    # Código de salida: 0 = éxito, 1 = hay fallos (útil para CI/CD)
    sys.exit(0 if pasados == total else 1)


if __name__ == "__main__":
    main()
