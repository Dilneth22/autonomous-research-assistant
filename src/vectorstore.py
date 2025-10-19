import os
import faiss
import pickle
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

# This will automatically use the GOOGLE_API_KEY from your .env file
try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
except Exception as e:
    print(f"Error initializing embedding model: {e}")
    embeddings = None

def create_vector_store(topic: str, documents: list[dict]):
    """
    Chunks, embeds, and stores documents in a new FAISS index for a specific topic.
    Returns the path to the new index folder.
    """
    if not embeddings:
        raise ConnectionError("Google Generative AI Embeddings model failed to initialize.")
        
    print(f"--- CREATING VECTOR STORE FOR TOPIC: {topic} ---")
    
    # Sanitize the topic to create a valid folder name
    sanitized_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
    index_path = os.path.join("indexes", sanitized_topic)
    
    if not os.path.exists(index_path):
        os.makedirs(index_path)

    # Prepare texts and their corresponding metadata
    texts_to_embed = []
    metadatas = []
    for doc in documents:
        texts_to_embed.append(doc['content'])
        metadatas.append({"source": doc['url']})

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    split_texts = text_splitter.create_documents(texts_to_embed, metadatas=metadatas)
    
    # Create FAISS index from the chunks
    vectorstore = FAISS.from_documents(documents=split_texts, embedding=embeddings)
    
    # Save the FAISS index
    vectorstore.save_local(index_path)
        
    print(f"--- VECTOR STORE CREATED AT: {index_path} ---")
    return index_path

def query_vector_store(query: str, index_path: str):
    """
    Queries an existing FAISS index to find relevant documents.
    """
    if not embeddings:
        raise ConnectionError("Google Generative AI Embeddings model failed to initialize.")
        
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index not found at path: {index_path}")

    # Load the FAISS index from disk
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

    # Perform similarity search
    results = vectorstore.similarity_search(query, k=5)
    return results

