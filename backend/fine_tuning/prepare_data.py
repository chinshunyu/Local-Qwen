import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))
from os.path import join as opj
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
from const import *


fine_tuning_path = opj(PROJECT_ROOT,'fine_tuning')
fine_tuning_datset_path = opj(fine_tuning_path, 'dataset')


class DataGenerator(object):
    def __init__(self, model_name_or_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.content = """
                你是一个物理学习问题生成机器人。你将生成用户可能会问到的物理学习相关的问题及相应的回答。
                生成的问答数据的格式是一个JSON,示例如下：
                ```
                    {
                        "instruction": "浮力定律是什么?",
                        "input": "",
                        "output": "浸在液体（或气体）中的物体受到液体（或气体）对它向上托的力叫浮力。根据阿基米德原理，浸在液体里的物体受到向上的浮力，浮力大小等于物体排开液体所受重力。 即F浮＝G液排＝ρ液gV排。（V排表示物体排开液体的体积） 浮力计算公式：F浮＝G-T＝ρ液gV排＝F上、下压力差 4．当物体漂浮时：F浮＝G物 且 ρ物G物 且 ρ物"
                    }
                ```
                注意：生成的json中包含三个字段：instruction，input，output。instruction是用户的问题，问题领域可以是天文、力学、电学、物理学习方法或者各类物理考试的技巧。input是一个空字符串，output是老师的回答，这个回答需要尽量详细，其中应该包含适量的例子进行解释，以便学生理解。
                """
        self.system_prompt = {
            "role": "system",
            "content": self.content
        }

    def generate_response(self, new_messages, max_length):
        history = [self.system_prompt] + new_messages
        input_ids = self.tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([input_ids], return_tensors="pt", padding=True, truncation=True).to('cuda')

        with torch.no_grad():
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=max_length,
                attention_mask=model_inputs.attention_mask,
                do_sample=True,
                top_p=0.97,
                top_k = 2000
            )

        generated_ids = [
            output_ids[len(model_inputs.input_ids[0]):] for output_ids in generated_ids
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]   
        print(response)

        return response


def do_match(txt):
        pattern = r'"instruction":\s*"([^"]*)",\s*"input":\s*"([^"]*)",\s*"output":\s*"(.*?)"'
        match = re.search(pattern, txt, re.DOTALL)
        if match:
            instruction = match.group(1)
            input_value = match.group(2)
            output_value = match.group(3)

            return {
                'instruction':instruction,
                'input':'',
                'output':output_value
            }
        else:
            print("未找到匹配项")

if __name__ == '__main__':
    dg = DataGenerator(model_name_or_path=MODEL_PATH)
    final_result = []
    exist_qestions = []
    message_en = [{'role': 'assistant', 'content': '您好,我是物理问题集生成器,有什么可以帮助您？'}, {'role': 'user', 'content': '请生成一条物理学习相关的问答数据'}]
    message_noen = [{'role': 'assistant', 'content': '您好,我是问答对话生成器,有什么可以帮助您？'}, {'role': 'user', 'content': '请生成一条问答数据'}]
    for i in range(20000):
        try:
            q_a: str =  dg.generate_response(new_messages=message_en, max_length=8000)
            q_a_dic = do_match(q_a)
            instruction = q_a_dic['instruction']
            print(instruction)
            print(q_a_dic)
            if instruction not in exist_qestions:
                final_result.append(q_a_dic)
                exist_qestions.append(instruction)
            else:
                print('问题已存在')
        except:
            continue
    
    with open(opj(fine_tuning_datset_path,'physics_qa.json'),'w',encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False)
    dg.content = """
请模拟一次提问与问答，提问者提出包含社会、科学等所有领域的问题，回答者不知道这个问题的答案，并礼貌地拒绝回答提问者的问题。
生成的问答数据的格式是一个JSON,示例如下（只是示例，请只参考格式，生成的内容与此无）：
```
    {
        "instruction": "勾股定理是什么?",
        "input": "",
        "output": "抱歉，我并不知道勾股定理是什么意思。我只是一位物理老师～"
    }
```
注意：生成的json中包含三个字段：instruction，input，output。instruction是提问，问题领域可以包罗万象，可以是天文地理，可以是人文艺术等。input是一个空字符串，output是老师的回答，这个回答需要保持礼貌，并拒绝正面回答instruct的问题，但是当instruct是关于日常问候或者询问老师个个人信息时，请正常回复，关于老师的个人信息的问题，请给出一名物理老师的信息。
"""
    dg.system_prompt['content'] = dg.content
    noen_qa_exsist_questions = []
    for i in range(20000):
        try:
            q_a: str =  dg.generate_response(new_messages=message_noen, max_length=8000)
            q_a_dic = do_match(q_a)
            instruction = q_a_dic['instruction']
            print(instruction)
            print(q_a_dic)
            if instruction not in noen_qa_exsist_questions:
                final_result.append(q_a_dic)
                noen_qa_exsist_questions.append(instruction)
            else:
                print('问题已存在')
        except:
            continue
    with open(opj(fine_tuning_datset_path,'no_physics_qa.json'),'w',encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False)