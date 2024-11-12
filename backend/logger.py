import os
from functools import wraps
from time import perf_counter
from loguru import logger
 
 
 
class MyLogger:
 
    def __init__(self, log_dir='logs', max_size=2, retention='7 days'):
        self.log_dir = log_dir
        self.max_size = max_size
        self.retention = retention
        self.logger = self.configure_logger()
 
    def configure_logger(self):
  
        os.makedirs(self.log_dir, exist_ok=True)
        shared_config = {
            'level': 'DEBUG',
            'enqueue': True,
            'backtrace': True,
            'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
        }
        logger.add(
            sink=f'{self.log_dir}/{{time:YYYY-MM-DD}}.log',
            rotation=f'{self.max_size} MB',
            retention=self.retention,
            **shared_config
        )
        logger.add(sink=self.get_log_path, **shared_config)
 
        return logger
 
    def get_log_path(self, message: str) -> str:

        log_level = message.record['level'].name.lower()
        log_file = f'{log_level}.log'
        log_path = os.path.join(self.log_dir, log_file)
 
        return log_path
 
    def __getattr__(self, level: str):
        return getattr(self.logger, level)
 
    def log_decorator(self, msg='Some errors happened!'):
 
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.info(f'-----------分割线-----------')
                self.logger.info(f'调用 {func.__name__} args: {args}; kwargs:{kwargs}')
                start = perf_counter()  # 开始时间
                try:
                    result = func(*args, **kwargs)
                    end = perf_counter()  # 结束时间
                    duration = end - start
                    self.logger.info(f'{func.__name__} 返回结果：{result}, 耗时：{duration:4f}s')
                    return result
                except Exception as e:
                    self.logger.exception(f'{func.__name__}: {msg}')
                    self.logger.info(f'-----------分割线-----------')
 
            return wrapper
 
        return decorator