from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

pdf_files = [
    "pdf-file-1.pdf",
    "pdf-file-2.pdf"
]

embeddings = OllamaEmbeddings(model="mxbai-embed-large")
db_location = "./chroma_company_docs"
add_documents = not os.path.exists(db_location)

vector_store = Chroma(
    collection_name="company_docs",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    all_documents = []

    for file_path in pdf_files:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        # Add source metadata to each document page
        for page in pages:
            page.metadata["source"] = os.path.basename(file_path)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        split_docs = splitter.split_documents(pages)
        all_documents.extend(split_docs)

    vector_store.add_documents(all_documents)

retriever = vector_store.as_retriever(search_kwargs={"k": 4})
