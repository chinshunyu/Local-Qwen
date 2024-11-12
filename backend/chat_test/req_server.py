from flask import Flask, request, jsonify, make_response
import requests
import uuid

app = Flask(__name__)

url = "http://127.0.0.1:5002/chat"

messages = [
    {"role": "assistant", "content": "您好,我是您的私人机器人助理,有什么可以帮助您？"}
]


def send_request(messages, current_message, user_id, bot_type='normal'):
    request_payload = {
        "messages": messages,
        "max_length": 512,
        "currentMessage": current_message,
        "bot_type": {"value": bot_type}
    }

    response = requests.post(url, json=request_payload, headers={
                             'Content-Type': 'application/json'}, cookies={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
        return data['response'], data['user_id']
    else:
        return None, None


@app.route('/chat', methods=['POST'])
def chat():
    global messages
    payload = request.json
    user_input = payload.get('currentMessage', {}).get('content', '')
    current_message = {"role": "user", "content": user_input}
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    messages.append(current_message)
    bot_type = payload.get('bot_type', {}).get('value', 'normal')
    assistant_response, new_user_id = send_request(
        messages, current_message, user_id, bot_type)
    if assistant_response is not None:
        messages.append({"role": "assistant", "content": assistant_response})
        resp = make_response(jsonify({"response": assistant_response}))
        resp.set_cookie('user_id', new_user_id, httponly=True,
                        secure=True, samesite='None', max_age=3600*24*30)
        return resp
    else:
        return jsonify({"error": "请求失败"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
