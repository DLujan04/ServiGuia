# -*- coding: utf-8 -*-
"""
verificar_gpt.py
Verifica si el servidor está usando GPT-4o real o el mock.
Envía un prompt que SOLO GPT-4o puede clasificar (no está en las palabras clave del mock).
"""
import urllib.request
import json

BASE_URL = "http://localhost:8000/api/diagnostico"

PRUEBAS = [
    {
        "prompt": "Hay cucarachas en toda la cocina",
        "etiqueta": "FUMIGACION (solo GPT-4o puede detectar esto)",
        "categoria_esperada_gpt": "fumigacion",
        "nota_mock": "El mock devolveria categoria=None (no reconocido)"
    },
    {
        "prompt": "El lavabo del bano gotea por el tubo de abajo",
        "etiqueta": "PLOMERIA ESPECIFICA (GPT-4o deberia detectar subcategoria)",
        "categoria_esperada_gpt": "plomeria.fugas_menores",
        "nota_mock": "El mock detectaria bano e iria a AMBIGUO con pregunta"
    },
    {
        "prompt": "Mi casa huele mucho a gas",
        "etiqueta": "GAS CRITICO (ambos deberan detectar esto)",
        "categoria_esperada_gpt": None,
        "nota_mock": "Ambos deberian dar nivel_urgencia=CRITICO"
    },
]


def probar(prompt, etiqueta):
    data = json.dumps({"descripcion": prompt}).encode()
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


print("=" * 65)
print("  VERIFICACION: GPT-4o real vs Mock")
print("=" * 65)

for p in PRUEBAS:
    print(f"\n[TEST] {p['etiqueta']}")
    print(f"  Prompt   : \"{p['prompt']}\"")
    try:
        res = probar(p["prompt"], p["etiqueta"])
        cat = res.get("categoria_detectada")
        nivel = res.get("nivel_urgencia")
        resumen = res.get("resumen_diagnostico", "")

        print(f"  Urgencia : {nivel}")
        print(f"  Categoria: {cat}")
        print(f"  Resumen  : {resumen}")

        if p["etiqueta"].startswith("FUMIGACION"):
            if cat and "fumigacion" in cat:
                print("  >>> RESULTADO: GPT-4o REAL esta activo (identifico fumigacion!)")
            else:
                print("  >>> RESULTADO: Parece que sigue usando el MOCK (no identifico fumigacion)")
                print(f"       (El mock devuelve categoria=None para este prompt)")

    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 65)
print("  Si la prueba FUMIGACION devolvio categoria='fumigacion'")
print("  entonces GPT-4o real esta funcionando correctamente.")
print("=" * 65)
