import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

DB_PATH = "./chroma_db_native"
BOOK_DIR = "static/books"
COLLECTION_NAME = "english_knowledge_base"

_client = None
_collection = None

def get_collection():
    """
    """
    global _client, _collection
    
    if _collection is not None:
        return _collection

    print(f"[RAG] Connecting to native ChromaDB at {DB_PATH}...")
    _client = chromadb.PersistentClient(path=DB_PATH)

    emb_fn = embedding_functions.DefaultEmbeddingFunction()

    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn
    )
    if _collection.count() == 0:
        print("[RAG] Database is empty. Processing PDFs... (One-time setup)")
        _initialize_database(_collection)
    else:
        print(f"[RAG] Loaded {_collection.count()} chunks from disk. (Fast load!)")

    return _collection

def _initialize_database(collection):
    if not os.path.exists(BOOK_DIR):
        os.makedirs(BOOK_DIR)
        print("[RAG] No books found.")
        return

    documents = []
    ids = []
    metadatas = []

    for filename in os.listdir(BOOK_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(BOOK_DIR, filename)
            print(f"  - Processing {filename}...")
            
            try:
                reader = PdfReader(file_path)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n"
                
                chunks = simple_text_splitter(full_text, chunk_size=500, overlap=50)
                
                for idx, chunk in enumerate(chunks):
                    documents.append(chunk)
                    ids.append(f"{filename}_{idx}")
                    metadatas.append({"source": filename})
                    
            except Exception as e:
                print(f"  ! Error reading {filename}: {e}")

    if documents:
        batch_size = 100
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        print(f"[RAG] Embedding {len(documents)} chunks...")
        for i in range(0, len(documents), batch_size):
            end = i + batch_size
            collection.add(
                documents=documents[i:end],
                ids=ids[i:end],
                metadatas=metadatas[i:end]
            )
        print("[RAG] Initialization complete. Data saved to disk.")

def simple_text_splitter(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks

def get_relevant_context(query):
    """
    """
    try:
        col = get_collection()
        
        results = col.query(
            query_texts=[query],
            n_results=2
        )
        
        if results['documents']:
            context_text = "\n\n".join(results['documents'][0])
            return context_text
        return ""
        
    except Exception as e:
        print(f"[RAG Error] {e}")
        return ""