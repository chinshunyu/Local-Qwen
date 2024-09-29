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

    def generate_response(self, user_id, new_messages, max_length):
        if user_id not in self.user_histories:
            self.user_histories[user_id] = []
        
        history = self.user_histories[user_id]
        history.extend(new_messages)
        
        # 只保留最近的 max_history 条消息
        history = history[-self.max_history:]

        # 只编码新消息
        input_ids = self.tokenizer.apply_chat_template(new_messages, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([input_ids], return_tensors="pt", padding=True, truncation=True).to('cuda')
        model_inputs = model_inputs.to('cuda')

        with torch.no_grad():
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=max_length,
                attention_mask=model_inputs.attention_mask,
                do_sample=False,
                # top_p=0.95,
                # top_k=50
            )

        generated_ids = [
            output_ids[len(model_inputs.input_ids[0]):] for output_ids in generated_ids
        ]

        # response = self.tokenizer.decode(generated_ids[0][len(model_inputs.input_ids[0]):], skip_special_tokens=True)
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]   
        history.append({'role': 'assistant', 'content': response})
        self.user_histories[user_id] = history
        
        return response

    def reset_history(self, user_id):
        if user_id in self.user_histories:
            self.user_histories[user_id] = []
            