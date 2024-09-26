from flask import Flask, request, jsonify
from chatbot import ChatBot
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


model_name_or_path = './qw/qw_model_file/qwen/Qwen2___5-7B-Instruct'
chatbot = ChatBot(model_name_or_path)

@app.route('/chat', methods=['POST'])
def generate_response():
    data = request.json
    messages = data.get('messages', [])
    max_length = data.get('max_length', 8000)
    response = chatbot.generate_response(messages, max_length)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)