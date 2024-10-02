import os
from data_service import load_or_create_faiss_index, add_vectors_to_faiss, preprocess_text, save_faiss_index
from openai_service import generate_embeddings_openai
import logging
import json
import numpy as np

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def on_starting(server):
    # Initialization logic before Gunicorn forks workers
    logger.info("Running initialization logic before Gunicorn forks workers.")
    
    # Load or create FAISS index
    index = load_or_create_faiss_index()

    # Retrieve the INITIAL_TEXTS environment variable as a string
    initial_texts_str = os.getenv('INITIAL_TEXTS', '[]')

    # Convert the string (which is in JSON format) into a Python list
    initial_texts = json.loads(initial_texts_str)
    
    all_embeddings = []
    for text in initial_texts:
        # Preprocess the text
        processed_text = preprocess_text(text)
        # Generate embeddings using OpenAI's embedding model
        embedding = generate_embeddings_openai(processed_text, os.getenv('OPENAI_EMBEDDING_MODEL'))

        if embedding is not None:
            embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
            all_embeddings.append(embedding_array)
            logger.info(f"Processed and generated embedding for text: {text}")
        else:
            logger.warning(f"Failed to generate embedding for text: {text}")

    if all_embeddings:
        # Stack embeddings and add them to the FAISS index
        all_embeddings_np = np.vstack(all_embeddings)
        add_vectors_to_faiss(index, all_embeddings_np)

    # Save the FAISS index after adding the embeddings
    save_faiss_index(index)

    logger.info("All texts have been processed and added to the FAISS index.")
