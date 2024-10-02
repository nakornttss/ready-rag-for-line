import faiss
import numpy as np
import os
import logging
from openai_service import generate_embeddings_openai
import pickle
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Path to store the FAISS index
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', 'faiss_index.bin')

# Function to create or load FAISS index
def load_or_create_faiss_index():
    vector_dimension = int(os.getenv('VECTOR_DIMENSION', '1536'))

    if os.path.exists(FAISS_INDEX_PATH):
        logger.info("Loading FAISS index from file...")
        with open(FAISS_INDEX_PATH, 'rb') as f:
            index = pickle.load(f)
        logger.info("Loaded FAISS index.")
    else:
        logger.info("Creating a new FAISS index...")
        # FAISS index for cosine similarity with 1536-dimensional vectors
        index = faiss.IndexFlatIP(vector_dimension)  # Cosine similarity
        logger.info("Created new FAISS index.")
    return index

# Function to save FAISS index to file
def save_faiss_index(index):
    # Ensure the directory exists before saving the FAISS index
    index_dir = os.path.dirname(FAISS_INDEX_PATH)
    
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)  # Create the directory if it doesn't exist
        logger.info(f"Created directory for FAISS index: {index_dir}")

    # Save the FAISS index to the specified file
    with open(FAISS_INDEX_PATH, 'wb') as f:
        pickle.dump(index, f)
    logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}.")

# Function to add vectors to the FAISS index
def add_vectors_to_faiss(index, vectors):
    logger.info(f"Adding {len(vectors)} vectors to FAISS index.")
    index.add(np.array(vectors, dtype=np.float32))
    save_faiss_index(index)

# Function to search similar texts using FAISS
def search_similar_texts(query, faiss_index, k=3):
    logger.info(f"Received query: {query}")

    # Load the INITIAL_TEXTS environment variable as a string
    initial_texts_str = os.getenv('INITIAL_TEXTS', '[]')

    # Convert the string (which is in JSON format) into a Python list
    initial_texts = json.loads(initial_texts_str)

    # Preprocess the query text
    processed_query = preprocess_text(query)
    logger.info(f"Processed query: {processed_query}")

    # Generate embeddings for the query
    query_embedding = generate_embeddings_openai(processed_query)
    logger.debug(f"Generated embedding for query: {query_embedding}")

    if not query_embedding:
        logger.error("Query embedding is empty or None. Aborting search.")
        return []

    query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    # Search in FAISS
    distances, indices = faiss_index.search(query_embedding, k)
    logger.info(f"Found {len(indices[0])} similar results with distances {distances[0]}.")

    # Map indices to texts from INITIAL_TEXTS
    similar_texts = [initial_texts[i] for i in indices[0] if i < len(initial_texts)]

    return similar_texts

def preprocess_text(text: str) -> str:
    return text
