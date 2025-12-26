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

## PASO 0: Instala uv (el manejador de paquetes moderno)

### ¿Qué es uv?

Es un manejador de paquetes de Python **ultra rápido** creado por Astral (los creadores de Ruff). Es hasta 100x más rápido que pip tradicional.

### Instala uv:

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verifica la instalación:

```bash
uv --version
```

**Deberías ver algo como: `uv 0.5.x`**

---

## PASO 1: Configura tu proyecto con uv

```bash
# Crea la carpeta del proyecto
mkdir mi-primer-agente-rag
cd mi-primer-agente-rag

# Inicializa el proyecto con uv
uv init
```

![/images/create-project-uv.gif](/images/create-project-uv.gif)

**Esto crea automáticamente:**

- Un entorno virtual en `.venv`
- Un archivo `pyproject.toml` para manejar dependencias
- Un archivo `.python-version` con la versión de Python

---

## PASO 2: Instala las librerías necesarias con uv

### ¿Qué harás?

Instalar todas las herramientas que tu agente necesita usando uv.

### ¿Por qué cada una?

- **langchain**: Framework para construir aplicaciones de IA
- **langchain-openai**: Conexión con GPT
- **chromadb**: Base de datos vectorial (el "cerebro" de tu agente)
- **pypdf**: Lector de archivos PDF
- **python-dotenv**: Manejo seguro de tu API Key

### Comando:

```bash
uv add langchain langchain-openai chromadb pypdf python-dotenv
```

![Install dependencies](/images/install-dep.gif)

---

## PASO 3: Protege tu API Key

### ¿Qué harás?

Crear un archivo `.env` para guardar tu API Key de forma segura.

### ¿Por qué?

**Nunca debes compartir tu API Key públicamente.** Usar `.env` evita que accidentalmente la subas a GitHub.

### Crea o abre .gitignore

`.gitignore`

```bash
.env
chroma_db/
.venv
```

![crea gitignore](/images/create-gitignore.gif)

Tu archivo debe verse asi:

### Crea o abre `.env` y agrega:

```
OPENAI_API_KEY=tu-api-key-aqui
```

si no sabes como crear tu api key aca te dejo un [video](https://www.youtube.com/watch?v=um4jXio7NjQ)

![env openai](/images/env-openai.gif)

**Guarda el archivo. Tu API Key ahora está protegida.**

---

## PASO 4: Importa las librerías

### ¿Qué harás?

Crear el archivo `agente_rag.py` e importar todas las herramientas.

### ¿Por qué cada import?

- `os` y `dotenv`: Para leer la API Key del archivo `.env`
- `OpenAIEmbeddings`: Convierte texto en vectores (números)
- `ChatOpenAI`: El modelo GPT que responderá preguntas
- `PyPDFLoader`: Lee archivos PDF
- `RecursiveCharacterTextSplitter`: Divide documentos grandes en pedazos
- `Chroma`: La base de datos vectorial
- `RetrievalQA`: La cadena RAG completa

### Código:

```python
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
```

---

## PASO 5: Carga tu API Key

### ¿Qué harás?

Leer la API Key del archivo `.env` de forma segura.

### ¿Por qué?

Necesitas autenticarte con OpenAI para usar GPT. Sin esto, el agente no funcionará.

### Código:

```python
# Cargar variables del archivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Verificar que existe
if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY en el archivo .env")
    exit()

print("✅ API Key cargada correctamente")
```

**Esto previene errores si olvidaste configurar el `.env`.**

---

## PASO 6: Carga el PDF

### Código:

```python
print("\n📄 Cargando el PDF...")
ruta_pdf = input("Escribe la ruta de tu PDF: ")

try:
    loader = PyPDFLoader(ruta_pdf)
    documentos = loader.load()
    print(f"✅ PDF cargado: {len(documentos)} páginas encontradas")
except Exception as e:
    print(f"❌ Error al cargar el PDF: {e}")
    exit()
```

## PASO 7: Divide el texto en chunks

### Código:

```python
print("\n✂️ Dividiendo el documento en partes más pequeñas...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documentos)
print(f"✅ Documento dividido en {len(chunks)} chunks")
```

- `chunk_size=1000`: Cada pedazo tiene máximo 1000 caracteres
- `chunk_overlap=200`: Hay 200 caracteres repetidos entre chunks para no perder contexto

**Un PDF de 5 páginas puede generar 20-30 chunks.**

**PyPDFLoader extrae el texto de cada página y crea un "documento" por página.**

---

## PASO 8: Crea embeddings y la base de datos vectorial

### ¿Qué harás?

Convertir cada chunk en un vector (lista de números) y guardarlo en ChromaDB.

### ¿Por qué?

Los embeddings representan el **significado** del texto como números. ChromaDB busca chunks con significados similares a tu pregunta usando matemáticas.

**Ejemplo:** "Python programming" y "codificación en Python" tienen vectores muy parecidos aunque las palabras sean diferentes.

### Código:

```python
print("\n🧠 Creando la base de conocimiento...")
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
print("✅ Base de conocimiento creada")
```

**Esto toma 10-30 segundos. Se crea una carpeta `chroma_db` con tu base de datos.**

---

## PASO 9: Inicializa el modelo GPT

### ¿Qué harás?

Configurar el modelo de lenguaje que responderá las preguntas.

### ¿Por qué estos parámetros?

- `model="gpt-3.5-turbo"`: Modelo rápido y económico (puedes usar gpt-4 si quieres)
- `temperature=0`: Respuestas precisas y consistentes (0 = menos creativo, 1 = más creativo)

### Código:

```python
print("\n🤖 Inicializando el modelo GPT...")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
```

---

## PASO 10: Crea la cadena RAG

### ¿Qué harás?

Conectar el modelo GPT con tu base de datos vectorial.

### ¿Por qué?

Aquí es donde sucede la magia del RAG:

1. Tu pregunta se convierte en vector
2. ChromaDB busca los 3 chunks más similares (`k=3`)
3. GPT recibe tu pregunta + esos 3 chunks como contexto
4. GPT responde basándose en ESE contenido específico

### Código:

```python
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

print("✅ ¡Agente RAG listo!")
```

**`chain_type="stuff"` significa que "mete" todos los chunks recuperados en el prompt.**

---

## PASO 11: Loop de preguntas

### ¿Qué harás?

Crear un bucle interactivo donde puedes hacer preguntas ilimitadas.

### ¿Por qué?

Permite conversar con tu documento de forma natural. Escribe preguntas, obtén respuestas, repite.

### Código:

```python
print("\n" + "="*60)
print("🎉 ¡TU AGENTE RAG ESTÁ FUNCIONANDO!")
print("="*60)
print("Escribe 'salir' para terminar\n")

while True:
    pregunta = input("💬 Tu pregunta: ")

    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("\n👋 ¡Hasta luego!")
        break

    if not pregunta.strip():
        print("⚠️ Por favor escribe una pregunta válida")
        continue

    print("\n🔍 Buscando en el documento...")
    try:
        respuesta = qa_chain.invoke({"query": pregunta})
        print(f"\n🤖 Respuesta:\n{respuesta['result']}\n")
        print("-" * 60 + "\n")
    except Exception as e:
        print(f"❌ Error al procesar la pregunta: {e}\n")
```

---

## 🎯 CÓDIGO COMPLETO

Crea un archivo `agente_rag.py` y copia todo esto:

```python
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# PASO 1: Cargar la API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY en el archivo .env")
    exit()

print("✅ API Key cargada correctamente")

# PASO 2: Cargar el PDF
print("\n📄 Cargando el PDF...")
ruta_pdf = input("Escribe la ruta de tu PDF: ")

try:
    loader = PyPDFLoader(ruta_pdf)
    documentos = loader.load()
    print(f"✅ PDF cargado: {len(documentos)} páginas encontradas")
except Exception as e:
    print(f"❌ Error al cargar el PDF: {e}")
    exit()

# PASO 3: Dividir el texto en chunks
print("\n✂️ Dividiendo el documento en partes más pequeñas...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documentos)
print(f"✅ Documento dividido en {len(chunks)} chunks")

# PASO 4: Crear embeddings y la base de datos vectorial
print("\n🧠 Creando la base de conocimiento...")
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
print("✅ Base de conocimiento creada")

# PASO 5: Crear el modelo de lenguaje
print("\n🤖 Inicializando el modelo GPT...")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# PASO 6: Crear la cadena RAG
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

print("✅ ¡Agente RAG listo!")

# PASO 7: Loop de preguntas
print("\n" + "="*60)
print("🎉 ¡TU AGENTE RAG ESTÁ FUNCIONANDO!")
print("="*60)
print("Escribe 'salir' para terminar\n")

while True:
    pregunta = input("💬 Tu pregunta: ")

    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("\n👋 ¡Hasta luego!")
        break

    if not pregunta.strip():
        print("⚠️ Por favor escribe una pregunta válida")
        continue

    print("\n🔍 Buscando en el documento...")
    try:
        respuesta = qa_chain.invoke({"query": pregunta})
        print(f"\n🤖 Respuesta:\n{respuesta['result']}\n")
        print("-" * 60 + "\n")
    except Exception as e:
        print(f"❌ Error al procesar la pregunta: {e}\n")
```

---

## ▶️ Ejecuta tu agente con uv

### Opción 1: Ejecución directa

```bash
uv run agente_rag.py
```

**uv automáticamente:**

- Activa el entorno virtual
- Verifica que todas las dependencias estén instaladas
- Ejecuta tu script

### Opción 2: Ejecutar en el entorno virtual

```bash
# Activa el entorno (si quieres trabajar interactivamente)
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Luego ejecuta normalmente
python agente_rag.py
```

### Ejemplo de uso:

```
✅ API Key cargada correctamente

📄 Cargando el PDF...
Escribe la ruta de tu PDF: manual_python.pdf
✅ PDF cargado: 10 páginas encontradas

✂️ Dividiendo el documento en partes más pequeñas...
✅ Documento dividido en 45 chunks

🧠 Creando la base de conocimiento...
✅ Base de conocimiento creada

🤖 Inicializando el modelo GPT...
✅ ¡Agente RAG listo!

============================================================
🎉 ¡TU AGENTE RAG ESTÁ FUNCIONANDO!
============================================================
Escribe 'salir' para terminar

💬 Tu pregunta: ¿De qué trata este documento?

🔍 Buscando en el documento...

🤖 Respuesta:
Este documento es un manual de Python que cubre los fundamentos del lenguaje...

------------------------------------------------------------

💬 Tu pregunta: salir

👋 ¡Hasta luego!
```
