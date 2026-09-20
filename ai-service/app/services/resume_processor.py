"""
Resume Processor Service

Pipeline: PDF -> Text Extraction -> Chunking -> Embeddings -> ChromaDB

Uses:
- PyPDFLoader for PDF text extraction
- RecursiveCharacterTextSplitter for semantic chunking
- HuggingFaceEmbeddings (all-MiniLM-L6-v2) for local embeddings
- ChromaDB for persistent vector storage
"""
import os
import uuid
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

# Initialize the embedding model once (it's loaded into memory)
_embeddings = None


def get_embeddings():
    """Lazy-load the embedding model to avoid loading it on import."""
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        logger.info("Embedding model loaded successfully")
    return _embeddings


def process_resume(file_path: str) -> dict:
    """
    Process a resume PDF through the full pipeline:
    1. Extract text from PDF
    2. Split into semantic chunks
    3. Generate embeddings
    4. Store in ChromaDB with a unique session_id

    Args:
        file_path: Path to the uploaded PDF file

    Returns:
        dict with session_id and num_chunks
    """
    # Generate a unique session ID for this resume's vector collection
    session_id = str(uuid.uuid4())

    # Step 1: Extract text from PDF
    logger.info(f"Extracting text from: {file_path}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    if not pages:
        raise ValueError("Could not extract any text from the PDF. The file may be scanned/image-based.")

    full_text = "\n".join([page.page_content for page in pages])
    logger.info(f"Extracted {len(pages)} pages, {len(full_text)} characters total")

    # Step 2: Split into chunks
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(pages)
    logger.info(f"Split into {len(chunks)} chunks")

    # Step 3 & 4: Generate embeddings and store in ChromaDB
    # Each resume gets its own collection identified by session_id
    persist_directory = os.path.join(CHROMA_PERSIST_DIR, session_id)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=f"resume_{session_id}",
        persist_directory=persist_directory
    )
    logger.info(f"Stored {len(chunks)} chunks in ChromaDB collection: resume_{session_id}")

    return {
        "session_id": session_id,
        "num_chunks": len(chunks),
        "full_text": full_text
    }


def get_retriever(session_id: str, k: int = 4):
    """
    Get a retriever for a specific resume session.

    Args:
        session_id: The session ID from resume processing
        k: Number of chunks to retrieve

    Returns:
        A LangChain retriever bound to the session's ChromaDB collection
    """
    persist_directory = os.path.join(CHROMA_PERSIST_DIR, session_id)

    vectorstore = Chroma(
        collection_name=f"resume_{session_id}",
        embedding_function=get_embeddings(),
        persist_directory=persist_directory
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_context(session_id: str, query: str, k: int = 4) -> str:
    """
    Retrieve relevant resume context for a given query.

    Args:
        session_id: The session ID from resume processing
        query: The search query (e.g., topic for question generation)
        k: Number of chunks to retrieve

    Returns:
        Concatenated relevant resume text
    """
    retriever = get_retriever(session_id, k)
    docs = retriever.invoke(query)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    logger.info(f"Retrieved {len(docs)} chunks for query: {query[:50]}...")
    return context
