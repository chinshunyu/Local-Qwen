import torch
from typing import List, Dict, Type, final
import re
from abc import ABCMeta, abstractmethod
from model import QwModel
from prompt import *
import weakref
from logger import MyLogger


LOGGER = MyLogger()


class FlyweightMeta(type):

    def __new__(mcs, name, parents, dct):
        dct['pool'] = weakref.WeakValueDictionary()
        return super().__new__(mcs, name, parents, dct)
    
    @staticmethod
    def _serialize_params(cls, *args, **kwargs):
        args_list = list(map(str, args))
        args_list.extend([str(kwargs), cls.__name__])
        key = ''.join(args_list)
        return key
    
    def __call__(cls, *args, **kwargs):
        key = FlyweightMeta._serialize_params(cls, *args, **kwargs)
        pool = getattr(cls, 'pool', {})

        instance = pool.get(key)
        if instance is None:
            instance = super().__call__(*args, **kwargs)
            pool[key] = instance
        return instance


class Bot():

    __metaclass__ = ABCMeta

    def __init__(self, qw_model: QwModel, max_history: int = 8) -> None:
        self.tokenizer = qw_model.tokenizer
        self.model = qw_model.model
        self.user_histories: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history

    @abstractmethod
    def generate_response(self, user_id: str, new_messages: List[Dict[str, str]], max_length:int) -> str:
        pass

    @abstractmethod
    def reset_history(self, user_id: str) -> None:
        pass
    
    @final
    def _prepare_history(self, user_id: str, new_messages: List[Dict[str, str]], system_prompt: Dict[str, str]) -> List[Dict[str, str]]:
        if user_id not in self.user_histories:
            self.user_histories[user_id] = [system_prompt]

        history = self.user_histories[user_id]
        history.extend(new_messages)
        history = [system_prompt] + history[1:][-self.max_history:]
        return history
    
    @final
    def _generate_response(self, history: List[Dict[str, str]], max_length: int) -> str:
        input_ids = self.tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([input_ids], return_tensors='pt', padding=True, truncation=True).to('cuda')

        with torch.no_grad():
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=max_length,
                attention_mask=model_inputs.attention_mask,
                do_sample=True,
                temperature=1.1,
                top_p=0.98,
                top_k=75,
            )

        generated_ids = [
            output_ids[len(model_inputs.input_ids[0]):] for output_ids in generated_ids
        ]

        response: str = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response


class ChatBot(Bot, metaclass = FlyweightMeta):

    def __init__(self, qw_model: QwModel, max_history: int = 8) -> None:
        super().__init__(qw_model, max_history)
        self.user_histories: Dict[str, List[Dict[str, str]]] = {}
        self.__repr__ = self.__str__
        self.system_prompt = {
            "role": "system",
            "content": CHAT_BOT_PROMPT
        }

    def __str__(self) -> str:
        return 'An physics AI assistant who helps students with any aspects aoubt physics learning.'

    def generate_response(self, user_id: str, new_messages: List[Dict[str, str]], max_length: int) -> str:
        LOGGER.debug(new_messages)
        history = self._prepare_history(user_id, new_messages, self.system_prompt)
        response = self._generate_response(history, max_length)
        history.append({'role': 'assistant', 'content': response})
        self.user_histories[user_id] = history

        return response

    def reset_history(self, user_id):
        if user_id in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]


class AstronomyBot(Bot, metaclass = FlyweightMeta):

    def __init__(self, qw_model, max_history: int = 8):
        super().__init__(qw_model, max_history)
        self.__repr__ = self.__str__
        self.system_prompt = {
            "role": "system",
            "content": ASTRONOMY_BOT_PROMPT
        }

    def __str__(self) -> str:
        return 'An astronomy AI teacher who helps students with astronomy learning.'

    def generate_response(self, user_id: str, new_messages: List[Dict[str, str]], max_length: int) -> str:

        history = self._prepare_history(user_id, new_messages, self.system_prompt)
        response: str = self._generate_response(history, max_length)
        response: str = response.replace('```markdown','').replace('```','')
        history.append({'role': 'assistant', 'content': response})
        self.user_histories[user_id] = history

        return response

    def reset_history(self, user_id):
        if user_id in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]
    
    def reset_history(self, user_id: str) -> None:
        if user_id in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]


class ElectricityBot(Bot, metaclass=FlyweightMeta):

    def __init__(self, qw_model, max_history: int = 8):
        super().__init__(qw_model, max_history)
        self.__repr__ = self.__str__
        self.system_prompt = {
            "role": "system",
            "content": ELECTRICITY_BOT_PROMPT
        }
        
    def __str__(self) -> str:
        return 'An electricity teacher who concentrates on helping users with electricity learning.'
 
    def generate_response(self, user_id: str, new_messages: List[Dict[str, str]], max_length: int) -> str:

        history = self._prepare_history(user_id, new_messages, self.system_prompt)
        response: str = self._generate_response(history, max_length)
        response: str = response.replace('```markdown','').replace('```','')
        history.append({'role': 'assistant', 'content': response})
        self.user_histories[user_id] = history

        return response

    def reset_history(self, user_id):
        if user_id in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]


class MechanicsBot(Bot, metaclass=FlyweightMeta):

    def __init__(self, qw_model, max_history: int = 8):
        super().__init__(qw_model, max_history)
        # self.user_histories: Dict[str, List[Dict[str, str]]] = {}
        self.__repr__ = self.__str__
        self.system_prompt = {
            "role": "system",
            "content": MECHANICS_EXAMINER_PROMPT
        }

    def __str__(self) -> str:
        return 'A mechanics teacher who concentrates on helping users with mechanics learning.'

    def generate_response(self, user_id: str, new_messages: List[Dict[str, str]], max_length: int) -> str:

        history = self._prepare_history(user_id, new_messages, self.system_prompt)
        response: str = self._generate_response(history, max_length)
        history.append({'role': 'assistant', 'content': response})
        self.user_histories[user_id] = history

        return response

    def reset_history(self, user_id):
        if user_id in self.user_histories:
            self.user_histories[user_id] = [self.system_prompt]

class BotShop(object):

    def __init__(self, bot_cls: Type[Bot]) -> None:
        self.bot_cls = bot_cls

    def buy_bot(self, qw_model: QwModel, max_history: int=8) -> Bot:
        bot = self.bot_cls(qw_model, max_history)
        return bot
