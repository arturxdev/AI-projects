# Tu Primer Agente RAG: Construye un Asistente IA que Lee PDFs

## ¿Qué vas a construir?

Vas a crear tu primer agente de inteligencia artificial capaz de **leer documentos PDF y responder preguntas** sobre su contenido. Es como tener un asistente personal que lee por ti y te explica lo que encuentra.

**Tiempo estimado:** 45-60 minutos

---

## Requisitos previos

✅ Python 3.10 o superior instalado  
✅ Un editor de código (VS Code recomendado)  
✅ API Key de OpenAI ([obtenerla aquí](https://platform.openai.com))  
✅ Un PDF para probar (cualquier documento)

---

## PASO 1: Instala uv (el manejador de paquetes moderno)

### ¿Qué es uv?

Es un manejador de paquetes de Python **ultra rápido** creado por Astral (los creadores de Ruff). Es hasta 100x más rápido que pip tradicional.

### Instala uv

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verifica la instalación

```bash
uv --version
```

**Deberías ver algo como: `uv 0.5.x`**

---

## PASO 2: Configura tu proyecto con uv

```bash
# Crea la carpeta del proyecto
mkdir rag-agent
cd rag-agent

# Inicializa el proyecto con uv
uv init
```

![/images/create-project-uv.gif](/images/create-project-uv.gif)

**Esto crea automáticamente:**

- Un entorno virtual en `.venv`
- Un archivo `pyproject.toml` para manejar dependencias
- Un archivo `.python-version` con la versión de Python

---

## PASO 3: Instala las librerías necesarias con uv

### ¿Qué harás?

Instalar todas las herramientas que tu agente necesita usando uv.

### ¿Por qué cada una?

- **langchain**: Framework para construir aplicaciones de IA
- **langchain-openai**: Conexión con GPT
- **chromadb**: Base de datos vectorial (el "cerebro" de tu agente)
- **pypdf**: Lector de archivos PDF
- **python-dotenv**: Manejo seguro de tu API Key

### Comando

```bash
uv add chromadb langchain langchain-chroma langchain-community langchain-openai langchain-text-splitters pypdf python-dotenv
```

![Install dependencies](/images/install-dep.gif)

---

## PASO 4: Protege tu API Key

### ¿Qué harás?

Crear un archivo `.env` para guardar tu API Key de forma segura.

### ¿Por qué?

**Nunca debes compartir tu API Key públicamente.** Usar `.env` evita que accidentalmente la subas a GitHub.

### Crea o abre .gitignore

pega en ese archivo el siguiente contenido

`.gitignore`

```bash
.env
chroma_db/
.venv
```

![crea gitignore](/images/create-gitignore.gif)

Tu archivo debe verse asi:

### Crea o abre `.env` y agrega

```
OPENAI_API_KEY=tu-api-key-aqui
```

si no sabes como crear tu api key aca te dejo un [video](https://www.youtube.com/watch?v=um4jXio7NjQ)

![env openai](/images/env-openai.gif)

**Guarda el archivo. Tu API Key ahora está protegida.**

---

## PASO 5: Cargar el pdf

Aqui necesitas tu archivo pdf de donde se van hacer las preguntas, puedes tomar mi archivo .

este archivo debe estar posicionado en la raiz del proyecto

### ¿Qué harás?

Crear el archivo `main.py`

### ¿Por qué cada import?

- `os` y `dotenv`: Para leer la API Key del archivo `.env`
- `OpenAIEmbeddings`: Convierte texto en vectores (números)
- `ChatOpenAI`: El modelo GPT que responderá preguntas
- `PyPDFLoader`: Lee archivos PDF
- `RecursiveCharacterTextSplitter`: Divide documentos grandes en pedazos
- `Chroma`: La base de datos vectorial
- `RetrievalQA`: La cadena RAG completa

### Código

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

# Cargar variables del archivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Verificar que existe
if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY en el archivo .env")
    exit()

print("✅ API Key cargada correctamente")

# Configuración
ruta_pdf = "./pdf prueba.pdf"
persist_directory = "./chroma_db"

# Inicializar embeddings
embeddings = OpenAIEmbeddings()

# Verificar si ya existe la base de datos
if os.path.exists(persist_directory) and os.listdir(persist_directory):
    print("\n♻️  Base de conocimiento existente encontrada, cargando...")
    vectorstore = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    print("✅ Base de conocimiento cargada desde disco")
else:
    print("\n📄 No se encontró base de conocimiento, procesando PDF...")
    print(f"📄 Cargando el PDF: {ruta_pdf}")

    try:
        loader = PyPDFLoader(ruta_pdf)
        documentos = loader.load()
        print(f"✅ PDF cargado: {len(documentos)} páginas encontradas")
    except Exception as e:
        print(f"❌ Error al cargar el PDF: {e}")
        exit()

```

## PASO 6: Divide el texto en chunks

### Código

```python
    print("\n✂️ Dividiendo el documento en partes más pequeñas...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documentos)
    print(f"✅ Documento dividido en {len(chunks)} chunks")
```

- `chunk_size=1000`: Cada pedazo tiene máximo 1000 caracteres
- `chunk_overlap=200`: Hay 200 caracteres repetidos entre chunks para no perder contexto

**Un PDF de 5 páginas puede generar 20-30 chunks.**

**PyPDFLoader extrae el texto de cada página y crea un "documento" por página.**

---

## PASO 7: Crea embeddings y la base de datos vectorial

```python
    print("\n🧠 Creando la base de conocimiento...")
    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=persist_directory
    )
    print("✅ Base de conocimiento creada y guardada")
```

**Esto toma 10-30 segundos. Se crea una carpeta `chroma_db` con tu base de datos.**

---

## PASO 8: Inicializa el modelo GPT

### ¿Por qué estos parámetros?

- `model="gpt-3.5-turbo"`: Modelo rápido y económico (puedes usar gpt-4 si quieres)
- `temperature=0`: Respuestas precisas y consistentes (0 = menos creativo, 1 = más creativo)

### Código

```python
print("\n🤖 Inicializando el modelo GPT...")
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vectorstore.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [retrieve_context]
prompt = (
    "Tienes acceso a una tool que te da informacion de un pdf , responde apartir de esa information "
    "Usa la tool para responder las dudas del usuario, se claro y conciso."
)
model = init_chat_model("gpt-4.1")
agent = create_agent(model, tools, system_prompt=prompt)
```

---

## PASO 9: Probar el agente

### ¿Qué harás?

vamos a probar el agente para validar que esta conectado correctamente

```python
query = "Que fue lo que paso con softbank el dia de hoy"

res = agent.invoke({"messages": [("user", query)]})
print(res["messages"][0].pretty_print())
print(res["messages"][-1].pretty_print())
```

Una vez ejecutada la prueba comenta, las tres líneas anteriores solo era para probar

ejecuta el script para validar el funcionamiento

```shell
uv run main.py
```

Te debería dar un resultado como este

```shell
✅ API Key cargada correctamente

📄 No se encontró base de conocimiento, procesando PDF...
📄 Cargando el PDF: ./pdf prueba.pdf
✅ PDF cargado: 2 páginas encontradas

✂️  Dividiendo el documento en partes más pequeñas...
✅ Documento dividido en 8 chunks

🧠 Creando la base de conocimiento...
✅ Base de conocimiento creada y guardada

🤖 Inicializando el modelo GPT...
================================ Human Message =================================

Que fue lo que paso con softbank el dia de hoy
None
================================== Ai Message ==================================

Hoy, SoftBank anunció la adquisición definitiva de DigitalBridge Group por aproximadamente 4.000 millones de dólares. Este movimiento estratégico tiene como principal objetivo escalar la infraestructura de inteligencia artificial de próxima generación. Con la compra, SoftBank busca expandir su capacidad en centros de datos y conectividad, elementos cruciales para soportar la creciente demanda de cómputo necesaria para los modelos de lenguaje a gran escala que han dominado el 2025.

Masayoshi Son, líder de SoftBank, refuerza así su apuesta por una "superinteligencia artificial" que requiere una sólida base física y global para operar sin latencia.
None
```

---

## PASO 10: Loop de preguntas

### ¿Qué harás?

Crear un bucle interactivo donde puedes hacer preguntas ilimitadas.
Para esto comenta, las tres líneas anteriores solo era para probar

```python
print("🎉 ¡TU AGENTE RAG ESTÁ FUNCIONANDO!")
print("Escribe 'salir' para terminar\n")

while True:
    pregunta = input("💬 Tu pregunta: ")

    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("\n👋 ¡Hasta luego!")
        break

    if not pregunta.strip():
        print("⚠️ Por favor escribe una pregunta válida")
        continue

    print("\n🔍 Buscando en el documento...")
    try:
        respuesta = agent.invoke({"messages": [("user", pregunta)]})
        print(respuesta["messages"][-1].pretty_print())
    except Exception as e:
        print(f"❌ Error al procesar la pregunta: {e}\n")

```

---

## 🎯 CÓDIGO COMPLETO

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

# Cargar variables del archivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Verificar que existe
if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY en el archivo .env")
    exit()

print("✅ API Key cargada correctamente")

# Configuración
ruta_pdf = "./pdf prueba.pdf"
persist_directory = "./chroma_db"

# Inicializar embeddings
embeddings = OpenAIEmbeddings()

# Verificar si ya existe la base de datos
if os.path.exists(persist_directory) and os.listdir(persist_directory):
    print("\n♻️  Base de conocimiento existente encontrada, cargando...")
    vectorstore = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    print("✅ Base de conocimiento cargada desde disco")
else:
    print("\n📄 No se encontró base de conocimiento, procesando PDF...")
    print(f"📄 Cargando el PDF: {ruta_pdf}")

    try:
        loader = PyPDFLoader(ruta_pdf)
        documentos = loader.load()
        print(f"✅ PDF cargado: {len(documentos)} páginas encontradas")
    except Exception as e:
        print(f"❌ Error al cargar el PDF: {e}")
        exit()

    print("\n✂️ Dividiendo el documento en partes más pequeñas...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documentos)
    print(f"✅ Documento dividido en {len(chunks)} chunks")

    print("\n🧠 Creando la base de conocimiento...")
    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=persist_directory
    )
    print("✅ Base de conocimiento creada y guardada")


print("\n🤖 Inicializando el modelo GPT...")
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vectorstore.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [retrieve_context]
prompt = (
    "Tienes acceso a una tool que te da informacion de un pdf , responde apartir de esa information "
    "Usa la tool para responder las dudas del usuario, se claro y conciso."
)
model = init_chat_model("gpt-4.1")
agent = create_agent(model, tools, system_prompt=prompt)


query = "Que fue lo que paso con softbank el dia de hoy"

res = agent.invoke({"messages": [("user", query)]})
print(res["messages"][0].pretty_print())
print(res["messages"][-1].pretty_print())


print("🎉 ¡TU AGENTE RAG ESTÁ FUNCIONANDO!")
print("Escribe 'salir' para terminar\n")

while True:
    pregunta = input("💬 Tu pregunta: ")

    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("\n👋 ¡Hasta luego!")
        break

    if not pregunta.strip():
        print("⚠️ Por favor escribe una pregunta válida")
        continue

    print("\n🔍 Buscando en el documento...")
    try:
        respuesta = agent.invoke({"messages": [("user", pregunta)]})
        print(respuesta["messages"][-1].pretty_print())
    except Exception as e:
        print(f"❌ Error al procesar la pregunta: {e}\n")
```

---

## ▶️ Ejecuta tu agente con uv

```bash
uv run main.py
```

### Ejemplo de uso

```
✅ API Key cargada correctamente

♻️   Base de conocimiento existente encontrada, cargando...
✅ Base de conocimiento cargada desde disco

🤖 Inicializando el modelo GPT...
🎉 ¡TU AGENTE RAG ESTÁ FUNCIONANDO!
Escribe 'salir' para terminar

💬 Tu pregunta: que compro nvidia?

🔍 Buscando en el documento...
================================== Ai Message ==================================

Nvidia compró una participación superior al 4% en Intel, por la que desembolsó 5.000 millones de dólares. Esta operación forma parte de una reestructuración financiera respaldada por SoftBank y el gobierno de EE. UU. La alianza técnica y financiera entre ambas empresas busca asegurar que Intel continúe fabricando semiconductores de vanguardia, mientras que Nvidia garantiza una cadena de suministro de chips de inferencia más estable.
None
💬 Tu pregunta: salir

👋 ¡Hasta luego!
```
