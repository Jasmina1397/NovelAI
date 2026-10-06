import requests
import json

# Leer las instrucciones del editor
with open("prompts/editor.md", "r", encoding="utf-8") as file:
    instrucciones = file.read()

# Leer el capítulo
with open("novelas/Ejemplo_Novela_01/capitulos/capitulo_1.md", "r", encoding="utf-8") as file:
    capitulo = file.read()

# Construir el prompt
prompt = f"""
{instrucciones}

---

Ahora analiza el siguiente capítulo siguiendo todas las instrucciones anteriores.

CAPÍTULO:
{capitulo}
"""

# Enviar la petición a Ollama

print("NovelIA está analizando el capítulo...")
print("Qwen está trabajando. No cierres el programa...\n")
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:4b",
        "prompt": prompt,
        "stream": True
    },
    stream=True,
    timeout=600
)



# Mostrar la respuesta mientras se genera
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data.get("response", ""), end="", flush=True)

print()