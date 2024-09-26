import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class ChatBot:
    def __init__(self, model_name_or_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.history = []

        
    # def generate_response(self, messages, max_length):
    #     self.history.extend(messages)
    #     input_ids = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    #     model_inputs = self.tokenizer([input_ids], return_tensors="pt").to('cuda')
    #     generated_ids = self.model.generate(model_inputs.input_ids, max_new_tokens=max_length)
    #     generated_ids = [
    #         output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    #     ]
    #     response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    #     self.history.append({'role': 'assistant', 'content': response})
    #     return response
    def generate_response(self, new_messages, max_length):
        # 将新消息添加到历史记录中
        self.history.extend(new_messages)
        input_ids = self.tokenizer.apply_chat_template(self.history, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([input_ids], return_tensors="pt").to('cuda')
        generated_ids = self.model.generate(model_inputs.input_ids, max_new_tokens=max_length)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        self.history.append({'role': 'assistant', 'content': response})
        return response
    
    def reset_history(self):
        self.history = []