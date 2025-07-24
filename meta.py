from meta_ai_api import MetaAI
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/ask_precision_ai', methods=['POST'])
def process():
    data = request.json
    message = data.get("message", "none")
    ai = MetaAI()

    try:
        ai_response = ai.prompt(message)
        response_message = ai_response.get('message', 'No response from AI.')
    except Exception as e:
        response_message = f"Error processing request: {str(e)}"

    # Always return a JSON response
    return jsonify({"response": response_message})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 2223))
    app.run(host='0.0.0.0', port=port, debug=True)
