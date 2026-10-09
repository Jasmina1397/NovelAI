import requests
import json
import os
import time
from datetime import datetime
import shutil


def preparar_novela(nombre_novela):
    """Crea automáticamente la estructura básica de una novela."""

    carpetas = [
        "capitulos",
        "personajes",
        "relaciones",
        "escenas",
        "trama",
        "analisis/historial",
        "memoria",
    ]

    ruta_novela = os.path.join("novelas", nombre_novela)

    for carpeta in carpetas:
        ruta = os.path.join(ruta_novela, carpeta)
        os.makedirs(ruta, exist_ok=True)

    archivo_memoria = os.path.join(
        ruta_novela, "memoria", "hechos.md"
    )

    if not os.path.exists(archivo_memoria):
        with open(archivo_memoria, "w", encoding="utf-8") as file:
            file.write("")

    print(f"📁 Estructura preparada para: {nombre_novela}")



def listar_novelas():
    """Devuelve las novelas existentes dentro de la carpeta novelas."""

    carpeta_novelas = "novelas"
    os.makedirs(carpeta_novelas, exist_ok=True)

    novelas = []

    for nombre in os.listdir(carpeta_novelas):
        ruta = os.path.join(carpeta_novelas, nombre)

        if os.path.isdir(ruta):
            novelas.append(nombre)

    return sorted(novelas, key=str.casefold)


def elegir_novela():
    """Permite crear una novela o seleccionar una existente."""

    while True:
        print("\n📚 ¡Hola! Bienvenida a NovelAI.")
        print("¿Qué quieres hacer?")
        print("1. Crear una novela nueva")
        print("2. Revisar una novela existente")
        print("0. Salir")

        opcion = input("\nElige una opción: ").strip()

        if opcion == "1":
            nombre = input(
                "\n¿Cómo se llamará tu nueva novela? "
            ).strip()

            if not nombre:
                print("❌ El nombre no puede estar vacío.")
                continue

            if nombre in {".", ".."} or "/" in nombre or "\\" in nombre:
                print("❌ El nombre no puede contener rutas.")
                continue

            novelas = listar_novelas()

            if any(nombre.casefold() == n.casefold() for n in novelas):
                print("❌ Ya existe una novela con ese nombre.")
                continue

            preparar_novela(nombre)
            return nombre

        elif opcion == "2":
            novelas = listar_novelas()

            if not novelas:
                print("\n📭 Todavía no hay novelas creadas.")
                continue

            print("\n📚 Novelas disponibles:\n")

            for numero, nombre in enumerate(novelas, start=1):
                print(f"{numero}. {nombre}")

            seleccion = input(
                "\nEscribe el número de la novela: "
            ).strip()

            if not seleccion.isdigit():
                print("❌ Introduce un número de la lista.")
                continue

            indice = int(seleccion) - 1

            if 0 <= indice < len(novelas):
                return novelas[indice]

            print("❌ Ese número no corresponde a ninguna novela.")

        elif opcion == "0":
            return None

        else:
            print("❌ Opción no válida.")

# -----------------------------
# Configuración
# -----------------------------

NOVELA = "Ejemplo_Novela_01"
CAPITULO = "capitulo_1"
preparar_novela(NOVELA)

RUTA_PROMPT = "prompts/editor.md"
RUTA_PROMPT_MEMORIA = "prompts/memoria.md"

MODELO = "qwen3:4b" #estos dos datos cambiarán según el modelo
OLLAMA_URL = "http://localhost:11434/api/generate"

def analizar_capitulo(novela, capitulo):
    RUTA_CAPITULO = f"novelas/{novela}/capitulos/{capitulo}.md"
    RUTA_ANALISIS = f"novelas/{novela}/analisis/{capitulo}.md"
    RUTA_HISTORIAL = f"novelas/{novela}/analisis/historial"
    RUTA_MEMORIA = f"novelas/{novela}/memoria/hechos.md"
    RUTA_PROPUESTA_MEMORIA = f"novelas/{novela}/memoria/propuesta_{capitulo}.md"

# -----------------------------
# Inicio
# -----------------------------

    inicio = time.time()

    print("🤖 NovelAI iniciado.\n")

    # -----------------------------
    # Leer instrucciones del editor
    # -----------------------------

    with open(RUTA_PROMPT, "r", encoding="utf-8") as file:
        instrucciones = file.read()

    print("📖 Instrucciones del editor cargadas.")


    # -----------------------------
    # Leer instrucciones de memoria
    # -----------------------------

    with open(RUTA_PROMPT_MEMORIA, "r", encoding="utf-8") as file:
        instrucciones_memoria = file.read()

    print("🧠 Instrucciones de memoria cargadas.")



    # -----------------------------
    # Leer memoria existente
    # -----------------------------

    if not os.path.exists(RUTA_MEMORIA):
        os.makedirs(os.path.dirname(RUTA_MEMORIA), exist_ok=True)

        with open(RUTA_MEMORIA, "w", encoding="utf-8") as file:
            file.write("")

        print("📄 Archivo de memoria creado.")

    with open(RUTA_MEMORIA, "r", encoding="utf-8") as file:
        memoria_existente = file.read()

    print("📚 Memoria narrativa cargada.")

    # -----------------------------
    # Leer capítulo
    # -----------------------------

    with open(RUTA_CAPITULO, "r", encoding="utf-8") as file:
        capitulo = file.read()

    print("📚 Capítulo cargado.\n")



    # -----------------------------
    # Construir prompt de memoria
    # -----------------------------


    prompt = f"""
    {instrucciones}

    ---

    MEMORIA NARRATIVA EXISTENTE:
    {memoria_existente}

    ---

    CAPÍTULO:
    {capitulo}

    ---

    Analiza el capítulo siguiendo las instrucciones del editor.
    """

    prompt_memoria = f"""
    {instrucciones_memoria}
    
    ---
    
    MEMORIA EXISTENTE:
    {memoria_existente}
    
    ---
    
    CAPÍTULO:
    {capitulo}
    
    ---
    
    Analiza el capítulo siguiendo las instrucciones de memoria.
    Propón únicamente los cambios necesarios para mantener la continuidad.
    No modifiques directamente ningún archivo.
    """


    # -----------------------------
    # Crear carpetas de análisis
    # -----------------------------

    os.makedirs(os.path.dirname(RUTA_ANALISIS), exist_ok=True)


    # -----------------------------
    # Enviar petición a Ollama
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
                f"{capitulo}_{fecha}.md"
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


    # -----------------------------
    # Generar propuesta de memoria
    # -----------------------------

    os.makedirs(os.path.dirname(RUTA_PROPUESTA_MEMORIA), exist_ok=True)

    print("\n🧠 Analizando la memoria narrativa...")

    response_memoria = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt_memoria,
            "stream": True
        },
        stream=True,
        timeout=600
    )

    response_memoria.raise_for_status()

    propuesta = []

    for line in response_memoria.iter_lines():
        if line:
            data = json.loads(line)
            texto = data.get("response", "")

            if texto:
                propuesta.append(texto)

    propuesta_completa = "".join(propuesta)

    if not propuesta_completa.strip():
        print("❌ Qwen no ha generado una propuesta de memoria.")
    else:
        with open(RUTA_PROPUESTA_MEMORIA, "w", encoding="utf-8") as file:
            file.write(propuesta_completa)

        print("✅ Propuesta de memoria guardada en:")
        print(f"   {RUTA_PROPUESTA_MEMORIA}")
        print("📌 La memoria definitiva no se ha modificado.")