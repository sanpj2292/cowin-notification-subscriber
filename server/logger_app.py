import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "background.log"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_file_handler(logFileName:str=LOG_FILE):
   file_handler = TimedRotatingFileHandler(logFileName, when='midnight', encoding=None, delay=False)
   file_handler.setFormatter(FORMATTER)
   return file_handler

def get_logger(logger_name, needFileHandler:bool=False):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   now = datetime.now()
   formattedNow = now.strftime("%Y%m%d")
   output_filename = f'./logs/{logger_name}_{formattedNow}.log'
   os.makedirs(os.path.dirname(output_filename), exist_ok=True)
   if needFileHandler:
      logger.addHandler(get_file_handler(output_filename))
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger