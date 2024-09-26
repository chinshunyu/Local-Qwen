# python -m vllm.entrypoints.openai.api_server --model ~/qw_model_file/qwen/Qwen2___5-7B-Instruct  --served-model-name Qwen2.5-7B-Instruct --max-model-len=2048

from openai import OpenAI
openai_api_key = "sk-xxx"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_outputs = client.chat.completions.create(
    model="Qwen2.5-7B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "太阳到地球的距离有多远？"},
    ]
)
print(chat_outputs)