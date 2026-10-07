import requests
import json
import os
import time
from datetime import datetime
import shutil
# -----------------------------
# Configuración
# -----------------------------

NOVELA = "Ejemplo_Novela_01"
CAPITULO = "capitulo_1"

RUTA_PROMPT = "prompts/editor.md"
RUTA_CAPITULO = f"novelas/{NOVELA}/capitulos/{CAPITULO}.md"
RUTA_ANALISIS = f"novelas/{NOVELA}/analisis/{CAPITULO}.md"
RUTA_HISTORIAL = f"novelas/{NOVELA}/analisis/historial"


MODELO = "qwen3:4b" #estos dos datos cambiarán según el modelo
OLLAMA_URL = "http://localhost:11434/api/generate"


# -----------------------------
# Inicio
# -----------------------------

inicio = time.time()

print("🤖 NovelAI iniciado.\n")


# -----------------------------
# Leer instrucciones
# -----------------------------

with open(RUTA_PROMPT, "r", encoding="utf-8") as file:
    instrucciones = file.read()

print("📖 Instrucciones del editor cargadas.")


# -----------------------------
# Leer capítulo
# -----------------------------

with open(RUTA_CAPITULO, "r", encoding="utf-8") as file:
    capitulo = file.read()

print("📚 Capítulo cargado.\n")


# -----------------------------
# Construir prompt
# -----------------------------

prompt = f"""
{instrucciones}

---

Ahora analiza el siguiente capítulo siguiendo todas las instrucciones anteriores.

CAPÍTULO:
{capitulo}
"""


# -----------------------------
# Crear carpetas de análisis
# -----------------------------

os.makedirs(os.path.dirname(RUTA_ANALISIS), exist_ok=True)


# -----------------------------
# Enviar petición a Ollama
# o, en tu caso la herramienta que uses,
# yo uso la Ia local con Qwen, pero no olvides adaptarlo
# -----------------------------


print("📨 Enviando petición a Qwen...")

inicio_peticion = time.time()

response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODELO,
        "prompt": prompt,
        "stream": True
    },
    stream=True,
    timeout=600
)

response.raise_for_status()

fin_peticion = time.time()

print(f"✅ Petición enviada ({fin_peticion - inicio_peticion:.2f} s)\n")


# -----------------------------
# Recibir respuesta
# -----------------------------

print("🧠 Qwen está analizando el capítulo...\n")

analisis = []

for line in response.iter_lines():
    if line:
        data = json.loads(line)

        texto = data.get("response", "")

        if texto:
            analisis.append(texto)


# -----------------------------
# Comprobar respuesta
# -----------------------------

analisis_completo = "".join(analisis)

if not analisis_completo.strip():
    print("\n\n❌ Qwen no devolvió ningún análisis.")
    raise SystemExit(1)


print("\n\n✅ Análisis recibido correctamente.")


# -----------------------------
# Guardar análisis
# -----------------------------

print("💾 Guardando análisis...")

inicio_guardado = time.time()

# Si ya existe un análisis anterior, conservarlo en el historial
if os.path.exists(RUTA_ANALISIS):
    with open(RUTA_ANALISIS, "r", encoding="utf-8") as file:
        analisis_anterior = file.read()

    if analisis_anterior.strip():
        os.makedirs(RUTA_HISTORIAL, exist_ok=True)

        fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ruta_version = os.path.join(
            RUTA_HISTORIAL,
            f"{CAPITULO}_{fecha}.md"
        )

        shutil.copy2(RUTA_ANALISIS, ruta_version)

        print(f"📚 Versión anterior guardada en:")
        print(f"   {ruta_version}")

# Guardar el nuevo análisis como versión actual
with open(RUTA_ANALISIS, "w", encoding="utf-8") as file:
    file.write(analisis_completo)

fin_guardado = time.time()

print(f"✅ Análisis actual guardado en:")
print(f"   {RUTA_ANALISIS}")
print(f"   Tiempo de guardado: {fin_guardado - inicio_guardado:.2f} s")

# -----------------------------
# Final
# -----------------------------

tiempo_total = time.time() - inicio

print(f"\n🎉 Proceso terminado en {tiempo_total:.2f} segundos.")