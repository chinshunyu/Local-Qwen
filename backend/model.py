from os.path import join as opj
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel
from pathlib import Path
import sys
import configargparse


parser = configargparse.ArgParser(description='Configuration for a chatbot')
parser.add_argument('-c', '--config', is_config_file=True,
                    help='config file path', default='./config/config.ini')
parser.add_argument('--model_path', help='Path of the model')
parser.add_argument('--bot_type', help='Type of the bot')
parser.add_argument('--origins', nargs='+', help='List of allowed origins', required=True)

args = parser.parse_args()
MODEL_PATH = args.model_path


PROJECT_ROOT = Path(__file__).absolute().parents[0].absolute()

sys.path.insert(0, str(PROJECT_ROOT))
fine_tuning_path = opj(PROJECT_ROOT, 'fine_tuning')
lora_path = opj(fine_tuning_path, "output",
                "Qwen2.5_instruct_lora", "checkpoint-2712")


class QwModel(object):

    instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(QwModel, cls).__new__(cls)
        return cls.instance
    
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, torch_dtype=torch.bfloat16, device_map="auto"
        )
        model = PeftModel.from_pretrained(model, model_id=lora_path)
        self.model = model.to('cuda')


qw_model: QwModel = QwModel()
