"""
check_env.py — Diagnóstico rápido de variables de entorno y API key.
Ejecutar: python check_env.py
"""
from dotenv import load_dotenv
import os
import json

load_dotenv()

entorno   = os.environ.get("ENTORNO", "NO DEFINIDO")
api_key   = os.environ.get("OPENAI_API_KEY", "NO DEFINIDA")
modelo    = os.environ.get("OPENAI_MODEL", "gpt-5-nano")

print("=" * 60)
print("  DIAGNÓSTICO DE VARIABLES DE ENTORNO")
print("=" * 60)
print(f"  ENTORNO        : {entorno}")
print(f"  OPENAI_MODEL   : {modelo}")
print(f"  API_KEY inicio : {api_key[:25]}...")
print(f"  API_KEY válida : {api_key and not api_key.startswith('sk-XXXX')}")
print("=" * 60)

if entorno != "production":
    print("\n[PROBLEMA] ENTORNO no es 'production'.")
    print("  El servidor usa mock_llm en lugar de GPT-4o.")
    print("  Solución: edita tu .env y pon  ENTORNO=production")
elif api_key.startswith("sk-XXXX") or not api_key:
    print("\n[PROBLEMA] OPENAI_API_KEY no está configurada correctamente.")
else:
    print("\n[OK] Variables OK. Probando llamada real a OpenAI...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": "Di exactamente: FUNCIONANDO"}],
            max_tokens=10,
            temperature=0,
        )
        texto = resp.choices[0].message.content.strip()
        tokens_usados = resp.usage.total_tokens
        print(f"  Respuesta de GPT-4o : {texto}")
        print(f"  Tokens usados       : {tokens_usados}")
        print("\n[OK] La API key funciona correctamente!")
    except Exception as e:
        print(f"\n[ERROR] Fallo al llamar a OpenAI: {e}")

print("\n" + "=" * 60)
print("  DIAGNÓSTICO DEL ENDPOINT LOCAL")
print("=" * 60)
try:
    import urllib.request
    req_data = json.dumps({"descripcion": "Hay cucarachas en mi cocina"}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/api/diagnostico",
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resultado = json.loads(r.read())
    cat = resultado.get("categoria_detectada")
    nivel = resultado.get("nivel_urgencia")
    print(f"  Urgencia   : {nivel}")
    print(f"  Categoria  : {cat}")
    if cat == "fumigacion":
        print("\n  [OK] GPT-4o REAL está activo (detectó fumigacion)")
    else:
        print("\n  [MOCK] El servidor sigue usando el MOCK (no reconoció fumigacion)")
        print("  Solución: REINICIA el servidor para que cargue el .env actualizado")
except Exception as e:
    print(f"  [INFO] No se pudo conectar al servidor local: {e}")
    print("  (El servidor no está corriendo o cambió de puerto)")

print("=" * 60)
