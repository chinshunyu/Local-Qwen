import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
print(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from logger import MyLogger
from datasets import Dataset
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, DataCollatorForSeq2Seq, TrainingArguments, Trainer, GenerationConfig
import torch
# import os
from pathlib import Path
from peft import LoraConfig, TaskType, get_peft_model,PeftModel
import torch

LOGGER = MyLogger()
PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()


sys.path.insert(0, str(PROJECT_ROOT))
from os.path import join as opj
fine_tuning_path = opj(PROJECT_ROOT,'fine_tuning')

df_physics = pd.read_json(opj(fine_tuning_path, 'dataset','physics_qa.json'))
df_no_physics = pd.read_json(opj(fine_tuning_path, 'dataset','no_physics_qa.json'))
df = pd.concat([df_physics, df_no_physics])


ds = Dataset.from_pandas(df)


tokenizer = AutoTokenizer.from_pretrained('/root/model_files/qw_model_file/qwen/Qwen2___5-7B-Instruct', use_fast=False, trust_remote_code=True)

def process_func(example):
    MAX_LENGTH = 384
    input_ids, attention_mask, labels = [], [], []
    instruction = tokenizer(f"<|im_start|>system\n现在你要扮演一名物理专家<|im_end|>\n<|im_start|>user\n{example['instruction'] + example['input']}<|im_end|>\n<|im_start|>assistant\n", add_special_tokens=False)  # add_special_tokens 不在开头加 special_tokens
    response = tokenizer(f"{example['output']}", add_special_tokens=False)
    input_ids = instruction["input_ids"] + response["input_ids"] + [tokenizer.pad_token_id]
    attention_mask = instruction["attention_mask"] + response["attention_mask"] + [1]
    labels = [-100] * len(instruction["input_ids"]) + response["input_ids"] + [tokenizer.pad_token_id]  
    if len(input_ids) > MAX_LENGTH:
        input_ids = input_ids[:MAX_LENGTH]
        attention_mask = attention_mask[:MAX_LENGTH]
        labels = labels[:MAX_LENGTH]
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

tokenized_id = ds.map(process_func, remove_columns=ds.column_names)
tokenizer.decode(tokenized_id[0]['input_ids'])
tokenizer.decode(list(filter(lambda x: x != -100, tokenized_id[1]["labels"])))


model = AutoModelForCausalLM.from_pretrained('/root/model_files/qw_model_file/qwen/Qwen2___5-7B-Instruct', device_map="auto",torch_dtype=torch.bfloat16)
model.enable_input_require_grads()

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, 
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    inference_mode=False,
    r=8, # Lora 秩
    lora_alpha=32, 
    lora_dropout=0.1
)

model = get_peft_model(model, config)
model.print_trainable_parameters()
args = TrainingArguments(
    output_dir=opj(fine_tuning_path,"output","Qwen2.5_instruct_lora"),
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    logging_steps=10,
    num_train_epochs=6,
    save_steps=100, 
    learning_rate=1e-4,
    save_on_each_node=True,
    gradient_checkpointing=True
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_id,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
)

trainer.train()

LOGGER.info("Training finished.")

mode_path = "/root/model_files/qw_model_file/qwen/Qwen2___5-7B-Instruct"
lora_path = opj(fine_tuning_path,"output","Qwen2.5_instruct_lora","checkpoint-2712")
tokenizer = AutoTokenizer.from_pretrained(mode_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(mode_path, device_map="auto",torch_dtype=torch.bfloat16, trust_remote_code=True).eval()
model = PeftModel.from_pretrained(model, model_id=lora_path)


prompt = """
解释一下牛顿第三定律
"""
inputs = tokenizer.apply_chat_template([{"role": "user", "content": "假设你是一名物理专家"},{"role": "user", "content": prompt}],
                                       add_generation_prompt=True,
                                       tokenize=True,
                                       return_tensors="pt",
                                       return_dict=True
                                       ).to('cuda')
gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}
with torch.no_grad():
    outputs = model.generate(**inputs, **gen_kwargs)
    outputs = outputs[:, inputs['input_ids'].shape[1]:]
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    LOGGER.info(tokenizer.decode(outputs[0], skip_special_tokens=True))