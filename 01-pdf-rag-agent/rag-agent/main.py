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

# res = agent.invoke({"messages": [("user", query)]})
# print(res["messages"][0].pretty_print())
# print(res["messages"][-1].pretty_print())


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
