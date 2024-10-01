import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class ChatBot:
    def __init__(self, model_name_or_path, max_history=10):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.user_histories = {}
        self.max_history = max_history
        self.system_prompt = {
            "role": "system",
            # "content": "You are an English teacher AI assistant. You are from a company named Alfaright(阿尔法睿). Your only role is to help users with English language learning and answer questions related to English. Please only respond to queries about English language, grammar, vocabulary, pronunciation, or English learning strategies. If a user asks about topics unrelated to English, politely decline to answer and remind them that you're here to assist with English-related questions only."
            # "content": "You are an English teacher AI assistant. Your name is Alfaright(Chinese name 阿尔法睿). Your role is strictly limited to helping users with English language learning. You must only respond to queries about English language, grammar, vocabulary, pronunciation, or English learning strategies. If a user asks about any topic unrelated to English learning, you must refuse to answer and respond only in English with: 'I'm sorry, but I can only assist with English-related questions. Could you please ask something about English language or learning?'"
            "content": "你是一名擅长编程的AI助手"
        }

    def generate_response(self, user_id, new_messages, max_length):
        print('===================')
        print(new_messages)
        print('========================')
        if user_id not in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]
        
        history = self.user_histories[user_id]
        history.extend(new_messages)
        
        # 只保留最近的 max_history 条消息，但始终包括系统提示
        history = [self.system_prompt] + history[1:][-self.max_history:]

        # 编码整个历史，包括系统提示
        input_ids = self.tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([input_ids], return_tensors="pt", padding=True, truncation=True).to('cuda')

        with torch.no_grad():
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=max_length,
                attention_mask=model_inputs.attention_mask,
                do_sample=False,
            )

        generated_ids = [
            output_ids[len(model_inputs.input_ids[0]):] for output_ids in generated_ids
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]   
        history.append({'role': 'assistant', 'content': response})
        self.user_histories[user_id] = history
        
        return response

    def reset_history(self, user_id):
        if user_id in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]