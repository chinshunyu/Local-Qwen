from flask import Flask, request, jsonify, make_response
from chatbot import *
from flask_cors import CORS
import uuid
from gevent.pywsgi import WSGIServer
from gevent import monkey
import configargparse
from model import qw_model
from logger import MyLogger



LOGGER: MyLogger = MyLogger()


parser = configargparse.ArgParser(description='Configuration for the server')
parser.add_argument('-c', '--config', is_config_file=True,
                    help='config file path', default='./config/config.ini')
parser.add_argument('--origins', nargs='+', help='List of allowed origins', required=True)
parser.add_argument('--model_path', help='Path of the model')
parser.add_argument('--bot_type', help='Type of the bot')
args = parser.parse_args()


monkey.patch_all()
app: Flask = Flask(__name__)
app.secret_key = '123456'  # 使用一个更复杂的密钥

CORS(app, resources={r"/*": {
    'origins': args.origins,
    "supports_credentials": True
}})

chatbot_shop: BotShop = BotShop(ChatBot)
astronomy_bot_shop: BotShop = BotShop(AstronomyBot)
chatbot: ChatBot = chatbot_shop.buy_bot(qw_model=qw_model, max_history=8)
astronomy_chatbot: AstronomyBot = astronomy_bot_shop.buy_bot(
    qw_model=qw_model, max_history=8)
electricity_shop: BotShop = BotShop(ElectricityBot)
electricity_bot: ElectricityBot = electricity_shop.buy_bot(
    qw_model=qw_model, max_history=8)
mechanics_shop: BotShop = BotShop(MechanicsBot)
mechanics_bot: MechanicsBot = mechanics_shop.buy_bot(qw_model=qw_model, max_history=8)


@app.route('/chat', methods=['POST', 'OPTIONS'])
def generate_response():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin',
                             request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    data = request.json
    bot_type = data.get('bot_type', {'value': 'normal'}).get('value', 'normal')

    messages = data.get('messages', [])
    max_length = data.get('max_length', 8000)
    current_message = data.get('currentMessage', '')
    user_id = request.cookies.get('user_id')
    
    LOGGER.info(f'{user_id}:{current_message}')
    
    current_message = current_message['content']
    if not user_id:
        user_id = str(uuid.uuid4())
    if bot_type == 'normal':
        response = chatbot.generate_response(user_id, messages, max_length)
    elif bot_type == 'astronomy':
        response = astronomy_chatbot.generate_response(
            user_id, messages, current_message, max_length)
    elif bot_type == 'electricity':
        response = electricity_bot.generate_response(
            user_id, messages, max_length)
    elif bot_type == 'mechanics':
        response = mechanics_bot.generate_response(
            user_id, messages, 16000)
    else:
        return jsonify({'error': 'Invalid bot type'}), 400
    resp = make_response(jsonify({'response': response, 'user_id': user_id}))
    resp.headers.add('Access-Control-Allow-Origin',
                     request.headers.get('Origin', '*'))
    resp.headers.add('Access-Control-Allow-Credentials', 'true')
    resp.set_cookie('user_id', user_id, httponly=True,
                    secure=True, samesite='None', max_age=3600*24*30)
    
    LOGGER.info(f'bot: {user_id}->{response}')
    
    LOGGER.info(f"Setting cookie: user_id={user_id}")
    return resp


@app.route('/reset', methods=['POST'])
def reset_history():
    user_id = request.cookies.get('user_id')
    if user_id:
        chatbot.reset_history(user_id)
        astronomy_chatbot.reset_history(user_id)
        return jsonify({'message': f'History reset for user {user_id}'})
    else:
        return jsonify({'error': 'No user ID found'}), 400


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()
