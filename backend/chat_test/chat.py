import requests
import uuid
import configargparse


parser = configargparse.ArgParser(description='Configuration for a chatbot')
parser.add_argument('-c', '--config', is_config_file=True, help='config file path')
parser.add_argument('--bot_type', help='Type of the bot')
parser.add_argument('--model_path', help='Path of the model')
args = parser.parse_args()

bot_type = args.bot_type
url = "http://127.0.0.1:5006/chat"

messages = [
    {"role": "assistant", "content": "您好,我是您的私人机器人助手,有什么可以帮助您吗？"}
]

def send_message(user_input, user_id, bot_type='normal'):
    global messages
    current_message = {"role": "user", "content": user_input}
    messages.append(current_message)
    request_payload = {
        "messages": messages,
        "currentMessage": current_message,
        "bot_type": {"value": bot_type}
    }

    response = requests.post(url, json=request_payload, headers={'Content-Type': 'application/json'}, cookies={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
        messages.append({"role": "assistant", "content": data['response']})
        return data['response'], response.cookies.get('user_id')
    else:
        return f"请求失败: {response.status_code}, {response.text}", None

def chat(bot_type='normal'):
    user_id = str(uuid.uuid4())
    while True:
        user_input = input("you: ")
        print('\n')
        if user_input.lower() in ["exit", "quit"]:
            break
        assistant_response, new_user_id = send_message(user_input, user_id, bot_type)
        if new_user_id:
            user_id = new_user_id
        print(f"bot: {assistant_response}")
        print('\n')


if __name__ == "__main__":
    # python chat.py --config ../config/config.ini
    chat(bot_type)
