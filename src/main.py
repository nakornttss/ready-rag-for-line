from flask import Flask, request, jsonify, abort
from data_service import search_similar_texts, load_or_create_faiss_index
from line_service import verify_line_signature, send_line_reply
from openai_service import get_chat_completion_response
import logging
from gunicorn.app.base import BaseApplication

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Liveness check route
@app.route('/status/liveness', methods=['GET'])
def liveness():
    return jsonify({"status": "alive"}), 200

# Readiness check route
@app.route('/status/readiness', methods=['GET'])
def readiness():
    try:
        # Example check: Load FAISS index to confirm service is ready
        faiss_index = load_or_create_faiss_index()
        if faiss_index:
            return jsonify({"status": "ready"}), 200
        else:
            return jsonify({"status": "unready"}), 503
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({"status": "unready", "error": str(e)}), 503

@app.route('/webhook', methods=['POST'])
def webhook():
    if not verify_line_signature(request):
        logger.warning("Failed signature verification")
        return abort(403)

    data = request.get_json()

    if 'events' in data:
        for event in data['events']:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_message = event['message']['text']
                reply_token = event['replyToken']

                # Load FAISS index and find similar texts
                faiss_index = load_or_create_faiss_index()
                similar_texts = search_similar_texts(user_message, faiss_index)
                logger.info(f"Similar texts found: {similar_texts}")

                # Combine similar texts into a single string context
                combined_context = '. '.join(similar_texts)

                # Get a response from the chat completion API
                response_message = get_chat_completion_response(user_message, combined_context)

                if response_message:
                    send_line_reply(reply_token, response_message)
                else:
                    send_line_reply(reply_token, "Sorry, I couldn't process your request.")

    return jsonify({'status': 'success'})

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options):
        self.application = app
        self.options = options

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == '__main__':
    # Run the application with StandaloneApplication
    StandaloneApplication(app).run()
