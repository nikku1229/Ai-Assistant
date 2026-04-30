from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

DOCS_DIR = "D:\\Coding\\Project\\Self\\Ai Assistant\\backend\\data\\docs"
CHROMA_DIR = "D:\\Coding\\Project\\Self\\Ai Assistant\\backend\\data\\chroma"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

print("Embeddings load ho rahi hain...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Embeddings ready!")


def load_vectorstore():
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)


def add_document(file_path: str):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    vectorstore = load_vectorstore()
    vectorstore.add_documents(chunks)

    return len(chunks)


def search_docs(query: str, k=3):
    try:
        vectorstore = load_vectorstore()
        results = vectorstore.similarity_search(query, k=k)
        if not results:
            return ""
        return "\n\n".join([r.page_content for r in results])
    except Exception as e:
        print(f"Search error: {e}")
        return ""
