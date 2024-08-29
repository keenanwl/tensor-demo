from flask import Flask, request, jsonify
import requests
import numpy as np
import json
import tensorflow as tf
from werkzeug.middleware.proxy_fix import ProxyFix
from waitress import serve
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from data import text_data_arr

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Use ProxyFix to handle reverse proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

pad_sequences = tf.keras.preprocessing.sequence.pad_sequences
Tokenizer = tf.keras.preprocessing.text.Tokenizer

# Initialize tokenizer globally
tokenizer = Tokenizer()

# TODO: move to env: os.getenv('API_TOKEN')
# This is obviously not secure and for demo-only
API_TOKEN = "wApHyPeLdaNtORDownsEPIcKinARTHO"

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated


def generate_text(seed_text, server_ip, sequence_length, num_chars_to_generate, tokenizer):
    generated_text = seed_text

    for _ in range(num_chars_to_generate):
        token_list = tokenizer.texts_to_sequences([generated_text])
        token_list = pad_sequences(token_list, maxlen=sequence_length, padding="pre")

        payload = {
            "signature_name": "serving_default",
            "inputs": {
                "keras_tensor": token_list.tolist()
            }
        }

        json_payload = json.dumps(payload)
        headers = {"content-type": "application/json"}

        try:
            response = requests.post(f"http://{server_ip}/v1/models/model:predict", data=json_payload, headers=headers, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error in TensorFlow Serving request: {str(e)}")
            return f"Error: Unable to generate text. Please try again later. {str(e)}"

        result = response.json()
        predicted_probs = np.array(result['outputs'][0])

        # Use temperature to add randomness
        temperature = 1
        predicted_probs = np.log(predicted_probs) / temperature
        exp_preds = np.exp(predicted_probs)
        predicted_probs = exp_preds / np.sum(exp_preds)

        # Sample from the distribution instead of always choosing the most likely token
        predicted_token = np.random.choice(len(predicted_probs), p=predicted_probs)

        output_word = tokenizer.index_word.get(predicted_token, "")

        if output_word:
            generated_text += " " + output_word
        else:
            break  # Stop if we can't find a valid word

    return generated_text


@app.route('/api/generate_text', methods=['POST'])
@limiter.limit("10 per minute")
@token_required
def generate_text_endpoint():
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    seed_text = data.get('seed_text')
    if not seed_text:
        return jsonify({"error": "No seed text provided"}), 400

    # TODO: Endpoint needs securing
    server_url = os.getenv('DEFAULT_SERVER_IP')
    sequence_length = data.get('sequence_length', int(os.getenv('DEFAULT_SEQUENCE_LENGTH', 100)))
    num_chars_to_generate = data.get('num_chars_to_generate', int(os.getenv('DEFAULT_NUM_CHARS', 10)))

    generated_text = generate_text(seed_text, server_url, sequence_length, num_chars_to_generate, tokenizer)
    return jsonify({"generated_text": generated_text})


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Internal Server Error: {str(e)}")
    return jsonify({"error": "Internal Server Error. Please try again later."}), 500


def initialize_tokenizer(corpus):
    global tokenizer
    tokenizer = Tokenizer(char_level=True, lower=True)
    tokenizer.fit_on_texts(corpus)

    # Print vocabulary size for debugging
    print(f"Vocabulary size: {len(tokenizer.word_index)}")

def create_app():
    # Initialize tokenizer with your corpus
    initialize_tokenizer(text_data_arr)
    return app

if __name__ == '__main__':
    create_app()
    # Use Waitress as the development WSGI server
    serve(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))