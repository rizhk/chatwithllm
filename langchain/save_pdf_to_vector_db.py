from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEndpointEmbeddings
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

def save_docs_to_vectorstore(documents, vectorstore_name: str):
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.getenv("HF_TOKEN")
    )

    PGVector.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=vectorstore_name,
        connection_string=os.getenv("POSTGRES_URL")
    )

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