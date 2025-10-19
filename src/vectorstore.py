import os
import faiss
import pickle
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS # Corrected import

try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
except Exception as e:
    print(f"Error initializing embedding model: {e}")
    embeddings = None

def create_vector_store(topic: str, documents: list[dict]):
    """
    Chunks, embeds, and stores documents in a new FAISS index for a specific topic.
    Processes documents in small, slow batches to respect API rate limits.
    """
    if not embeddings:
        raise ConnectionError("Google Generative AI Embeddings model failed to initialize.")
        
    print(f"--- CREATING VECTOR STORE FOR TOPIC: {topic} ---")
    
    sanitized_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
    index_path = os.path.join("indexes", sanitized_topic)
    
    if not os.path.exists(index_path):
        os.makedirs(index_path)

    texts_to_embed = []
    metadatas = []
    for doc in documents:
        texts_to_embed.append(doc['content'])
        metadatas.append({"source": doc['url']})

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    split_texts = text_splitter.create_documents(texts_to_embed, metadatas=metadatas)
    
    if not split_texts:
        print("--- No text to embed. Skipping vector store creation. ---")
        return None

    # --- MORE ROBUST BATCHING LOGIC ---
    print(f"Embedding {len(split_texts)} chunks in small, slow batches to respect free-tier limits...")
    batch_size = 1 # Process 1 chunk at a time for maximum safety
    vectorstore = None

    for i in range(0, len(split_texts), batch_size):
        batch = split_texts[i:i + batch_size]
        
        try:
            if vectorstore is None:
                # Create the initial vector store with the very first batch
                vectorstore = FAISS.from_documents(documents=batch, embedding=embeddings)
            else:
                # Add subsequent batches to the existing store
                vectorstore.add_documents(batch)
                
            print(f"  - Embedded batch {i + 1}/{len(split_texts)}...")
            # Wait between each request to be extra safe with requests-per-minute limits
            time.sleep(2) 
        except Exception as e:
            print(f"  - Error embedding batch {i + 1}: {e}")
            print("  - Skipping this batch and continuing...")
            time.sleep(5) # Wait longer after an error
            continue
    # --- END OF NEW LOGIC ---
    
    if vectorstore:
        vectorstore.save_local(index_path)
        print(f"--- VECTOR STORE CREATED AT: {index_path} ---")
        return index_path
    else:
        print("--- Vector store creation failed because no chunks could be embedded. ---")
        return None

def query_vector_store(query: str, index_path: str):
    if not embeddings:
        raise ConnectionError("Google Generative AI Embeddings model failed to initialize.")
        
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index not found at path: {index_path}")

    # allow_dangerous_deserialization is required for loading FAISS indexes with pickle
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

    results = vectorstore.similarity_search(query, k=5)
    return results

