import os
import chromadb
from datetime import datetime

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.config import Settings, DEFAULT_DATABASE, DEFAULT_TENANT

app = FastAPI()

# Configurações do cliente
CHROMA_COLLECTION_NAME = 'meeting-assistant-768-dimensional'
CHROMA_HOST = os.getenv('CHROMA_HOST', '127.0.0.1')
CHROMA_PORT = int(os.getenv('CHROMA_PORT', 8005))


def chroma_client() -> chromadb.HttpClient:
    """Configura e retorna o cliente Chroma."""
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        ssl=False,
        headers=None,
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )


def embedding_model() -> OllamaEmbeddings:
    """Retorna o modelo de embedding."""
    return OllamaEmbeddings(model="nomic-embed-text")


def chroma_collection() -> Chroma:
    """Configura e retorna a coleção Chroma."""
    return Chroma(
        client=chroma_client(),
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_model(),
    )


def save_chunks(chunks: list[Document]) -> None:
    """Salva os chunks no vetor store."""
    try:
        vector_store = chroma_collection()
        vector_store.add_documents(chunks)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar chunks: {e}")


def split_text(document: Document) -> list[Document]:
    """Divide o texto em chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    return text_splitter.split_documents([document])


class UploadRequest(BaseModel):
    file_name: str
    file_id: str
    content: str
    process_date: str


@app.post("/upload")
def process_content(request: UploadRequest) -> dict:
    """Processa o conteúdo do upload."""
    try:
        formatted_content = request.content.replace('__', '\n')
        process_date = request.process_date or datetime.now().strftime("%Y-%m-%d")

        document = Document(
            id=request.file_id,
            page_content=formatted_content,
            metadata={
                "file_name": request.file_name,
                "process_date": process_date  # Usar a data extraída
            }
        )
        chunks = split_text(document)
        save_chunks(chunks)
        all_content = ''.join(chunk.page_content for chunk in chunks)

        return {
            "statusCode": 200,
            "body": all_content,
            "chunks": len(chunks),
            "metadata": document.metadata
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar conteúdo: {e}")


@app.get("/search")
def search_content(query: str, k: int = 5) -> list:
    """Realiza a busca de conteúdo com um número especificado de resultados."""
    try:
        vector_store = chroma_collection()
        results = vector_store.similarity_search(query=query, k=k)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar conteúdo: {e}")


@app.get("/deep_search")
def deep_search(
    query_texts: list[str],
    n_results: int = 10,
    where: dict = None,
    where_document: dict = None
) -> list:
    """Realiza uma busca profunda com múltiplas queries e filtros de metadados."""
    try:
        vector_store = chroma_collection()
        results = vector_store.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao realizar busca profunda: {e}"
        )
