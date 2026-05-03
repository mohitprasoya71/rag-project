# services/embedding_service.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from config import GOOGLE_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
import os


def get_embeddings():
    """Initialize Google Generative AI Embeddings."""
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
        output_dimensionality=768,
    )


def get_pinecone_index():
    """Initialize Pinecone client and ensure index exists."""
    EXPECTED_DIMENSION = 768
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it doesn't exist
    existing_indexes = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EXPECTED_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    else:
        index_info = pc.describe_index(PINECONE_INDEX_NAME)
        if getattr(index_info, "dimension", None) != EXPECTED_DIMENSION:
            raise ValueError(
                f"Pinecone index '{PINECONE_INDEX_NAME}' has dimension {getattr(index_info, 'dimension', 'unknown')} "
                f"but embeddings are {EXPECTED_DIMENSION}-dimensional. "
                "Delete or recreate the index with the correct dimension."
            )

    return pc.Index(PINECONE_INDEX_NAME)


def load_and_chunk_pdf(pdf_path: str) -> list:
    """
    Load a PDF and split it into chunks.
    Returns a list of LangChain Document objects.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    chunks = splitter.split_documents(documents)
    return chunks


def embed_and_store(chunks: list, filename: str) -> int:
    """
    Embed chunks and store them in Pinecone.
    Adds filename as metadata for filtering.
    Returns number of chunks stored.
    """
    embeddings = get_embeddings()

    # Add filename metadata to each chunk
    for chunk in chunks:
        chunk.metadata["source_file"] = filename

    # Store in Pinecone
    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME
    )

    return len(chunks)


def get_vectorstore():
    """Load existing Pinecone vector store for querying."""
    embeddings = get_embeddings()
    return PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings
    )