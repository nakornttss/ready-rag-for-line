import os
import numpy as np
import requests  
import json      
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Function to generate embeddings using OpenAI API via HTTP POST request
def generate_embeddings_openai(text, model_name=os.getenv('OPENAI_EMBEDDING_MODEL')):
    """
    Generates embeddings (vectors) using the OpenAI API via an HTTP POST request.
    """
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"  # Load API key from config
    }
    data = {
        "input": text,
        "model": model_name  # Use the passed model name
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()

        # Extract and return the embedding from the response
        embeddings = result['data'][0]['embedding']
        logger.info(f"Dimension of the embedding: {len(embeddings)}")

        return embeddings
    except requests.exceptions.HTTPError as http_err:        
        logger.warning(f"HTTP error occurred: {http_err}")
    except Exception as e:
        logger.warning(f"Error generating embeddings with OpenAI: {e}")
        return None

def get_chat_completion_response(user_question, context):
    """
    Sends the user question and the retrieved context to OpenAI Chat Completion API.
    """
    url = "https://api.openai.com/v1/chat/completions"
    
    # Log the API URL
    logger.info(f"Sending request to OpenAI API: {url}")

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"  # Set the OpenAI API Key from the config
    }
    
    # Log the headers
    logger.debug(f"Request headers: {headers}")

    # Prepare the messages payload
    messages = [
        {"role": "system", "content": "คุณคือพนักงานของบริษัท ที.ที.ซอฟแวร์ โซลูชั่น จำกัด (T.T.Software Solution Co.,Ltd). กรุณาตอบคำถามเกี่ยวกับบริษัทฯ เป็นภาษาไทย โดยอ้างอิงจาก รายละเอียดที่เกี่ยวข้อง. คุณเป็นผู้ชาย."},
        {"role": "system", "content": f"รายละเอียดที่เกี่ยวข้อง: {context}"},
        {"role": "user", "content": user_question},        
    ]

    # Log the messages payload
    logger.debug(f"Messages: {json.dumps(messages, ensure_ascii=False, indent=2)}")

    # Prepare the data payload
    data = {
        "model": os.getenv('CHAT_COMPLETION_MODEL'),  # Use model from config
        "messages": messages,
        "temperature": float(os.getenv('CHAT_COMPLETION_TEMPERATURE', 0.7))  # Default temperature is 0.7 if not set
    }
    
    # Log the full data payload
    logger.debug(f"Request data payload: {json.dumps(data, ensure_ascii=False, indent=2)}")

    try:
        # Send the POST request to OpenAI API
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # Log response status code
        logger.info(f"Response status code: {response.status_code}")
        
        # Check if the response was successful
        response.raise_for_status()

        # Log and return the result
        result = response.json()
        logger.debug(f"OpenAI response: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result['choices'][0]['message']['content']
    
    except requests.exceptions.HTTPError as http_err:
        # Log the detailed error response
        logger.error(f"HTTP error occurred: {http_err}")
        logger.error(f"Response content: {response.text}")
    except Exception as e:
        logger.error(f"Error generating chat completion with OpenAI: {e}")
    
    return None
