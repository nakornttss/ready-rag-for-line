import hashlib
import base64
import hmac
import os
import numpy as np
import requests  
import json      
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Function to send a reply to LINE user
def send_line_reply(reply_token, message):
    """
    Sends a reply message back to the user via the LINE Messaging API.
    """
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"  # LINE access token from config
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        logger.info('Reply sent successfully.')
    else:
        logger.warning(f"Failed to send reply: {response.status_code}, {response.text}")

def verify_line_signature(request):
    # Extract header signature
    header_signature = request.headers.get('X-Line-Signature')
    logger.info(f"Header signature: {header_signature}")

    # Get the body of the request
    body = request.get_data(as_text=True)
    logger.debug(f"Request body: {body}")

    # Compute the HMAC-SHA256 hash of the request body using LINE channel secret
    secret = os.getenv('LINE_CHANNEL_SECRET').encode('utf-8')
    hash = hmac.new(secret, body.encode('utf-8'), hashlib.sha256).digest()

    # Compute the base64 encoded signature
    computed_signature = base64.b64encode(hash).decode()
    logger.info(f"Computed signature: {computed_signature}")

    # Compare and log the result
    if header_signature == computed_signature:
        logger.info("Signature verification passed.")
    else:
        logger.error("Signature verification failed. Header and computed signatures do not match.")

    return header_signature == computed_signature