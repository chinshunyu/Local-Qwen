#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File	:server.py
@Time	:2024/09/25 18:16:43
@Author :JohnCachy
@Mail	:junyong.chen@iston.ai
'''

# from flask import Flask, request, jsonify
# from chatbot import ChatBot
# from flask_cors import CORS
# app = Flask(__name__)
# CORS(app)


# model_name_or_path = '/data/cjy/qw/qw_model_file/qwen/Qwen2___5-7B-Instruct'
# chatbot = ChatBot(model_name_or_path)

# @app.route('/chat', methods=['POST'])
# def generate_response():
#     data = request.json
#     messages = data.get('messages', [])
#     max_length = data.get('max_length', 8000)
#     response = chatbot.generate_response(messages, max_length)
#     return jsonify({'response': response})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

###########


# from flask import Flask, request, jsonify
# from chatbot import ChatBot
# from flask_cors import CORS
# import uuid  # 新增：用于生成唯一用户ID

# app = Flask(__name__)
# CORS(app)

# model_name_or_path = '/data/cjy/qw/qw_model_file/qwen/Qwen2___5-7B-Instruct'
# chatbot = ChatBot(model_name_or_path)

# @app.route('/chat', methods=['POST'])
# def generate_response():
#     data = request.json
#     messages = data.get('messages', [])
#     max_length = data.get('max_length', 8000)
#     user_id = data.get('user_id')  # 新增：从请求中获取用户ID
    
#     if not user_id:
#         user_id = str(uuid.uuid4())  # 如果没有提供用户ID，则生成一个新的

#     response = chatbot.generate_response(user_id, messages, max_length)
#     return jsonify({'response': response, 'user_id': user_id})  # 返回响应和用户ID

# @app.route('/reset', methods=['POST'])  # 新增：重置聊天历史的路由
# def reset_history():
#     data = request.json
#     user_id = data.get('user_id')
#     if user_id:
#         chatbot.reset_history(user_id)
#         return jsonify({'message': f'History reset for user {user_id}'})
#     else:
#         return jsonify({'error': 'User ID is required'}), 400

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify, make_response
from chatbot import ChatBot
from flask_cors import CORS
import uuid
import time

app = Flask(__name__)
app.secret_key = '123456'  # 使用一个更复杂的密钥

# 修改 CORS 设置
# CORS(app, resources={r"/*": {"origins": ["http://192.168.10.225:9100"], "supports_credentials": True}})
CORS(app, resources={r"/*": {
    "origins": ["https://84a7-139-227-188-50.ngrok-free.app", "http://192.168.10.225:9100"],
    "supports_credentials": True
}})

model_name_or_path = '/data/cjy/qw/qw_model_file/qwen/Qwen2___5-7B-Instruct'
chatbot = ChatBot(model_name_or_path)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def generate_response():
    if request.method == 'OPTIONS':
        # 预检请求处理
        response = make_response()
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    data = request.json

    messages = data.get('messages', [])
    max_length = data.get('max_length', 8000)
    current_message = data.get('currentMessage', '')
    user_id = request.cookies.get('user_id')
    print('~~~~~~~~~~~')
    print(f'{user_id}:{current_message}')
    print('~~~~~~~~~~~~~')

    if not user_id:
        user_id = str(uuid.uuid4())

    response = chatbot.generate_response(user_id, messages, max_length)
    resp = make_response(jsonify({'response': response, 'user_id': user_id}))
    # resp.set_cookie('user_id', user_id, httponly=True, secure=False, samesite='Lax', max_age=3600*24*30)
    resp.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    resp.headers.add('Access-Control-Allow-Credentials', 'true')
    resp.set_cookie('user_id', user_id, httponly=True, secure=True, samesite='None', max_age=3600*24*30)
    print('<<<<<<<<<<<<<<<<<<<<<')
    print(f'bot: {user_id}->{response}')
    print('>>>>>>>>>>>>>>>>>>>>>>')
    print(f"Setting cookie: user_id={user_id}")
    return resp

@app.route('/reset', methods=['POST'])
def reset_history():
    user_id = request.cookies.get('user_id')
    if user_id:
        chatbot.reset_history(user_id)
        return jsonify({'message': f'History reset for user {user_id}'})
    else:
        return jsonify({'error': 'No user ID found'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)