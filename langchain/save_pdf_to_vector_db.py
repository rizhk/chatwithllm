from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector as PGVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from sqlalchemy import create_engine
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()

def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    return loader.load()

def split_text(documents, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

def get_embeddings_object():
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.getenv("HF_TOKEN")
    )
    
    return embeddings
        

def save_docs_to_vectorstore(chunks, vectorstore_name: str):
    embeddings = get_embeddings_object()
    
    CONNECTION_STRING = os.getenv("POSTGRES_URL")
    # Create engine
    engine = create_engine(CONNECTION_STRING)

    PGVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=vectorstore_name,
        connection=engine
    )
    
def getPgVectorConnection():
    CONNECTION_STRING = os.getenv("POSTGRES_URL")
    COLLECTION_NAME = "pdf_embeddings"
    embeddings = get_embeddings_object()

    # Create engine
    engine = create_engine(CONNECTION_STRING)

    # Initialize PGVector with the new syntax
    vectorstore = PGVectorStore(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=engine,
        use_jsonb=True  # Recommended for better filtering
    )

    return vectorstore

def save_pdf_in_vector_store():
    file_path = os.path.abspath(os.getenv("FILE_PATH"))
    documents = load_pdf(file_path)
    if not documents:
        print("No documents found in the PDF.")
        return

    split_docs = split_text(documents)
    vectorstore_name = "pdf_embeddings"
    save_docs_to_vectorstore(split_docs, vectorstore_name)
    print(f"✅ Saved {len(split_docs)} chunks to '{vectorstore_name}'")

if __name__ == "__main__":
    save_pdf_in_vector_store()